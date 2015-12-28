# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django import forms
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import UploadedCrash
from base.models import Product, Version

import os, uuid
import string

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
import traceback

class UploadFileForm(forms.Form):
    upload_file_minidump = forms.FileField()
    AdapterDeviceId = forms.CharField(required = False)
    AdapterVendorId = forms.CharField(required = False)
    Version = forms.CharField()
    ProductName = forms.CharField()


class InvalidProductException(Exception):
    def __init__(self, product):
        self.product = product

    def __str__(self):
        return "Invalid ProductName: " + self.product

class InvalidVersionException(Exception):
    def __init__(self, version, product):
        self.version = version
        self.product = product

    def __str__(self):
        return "Invalid Version: " + self.version + " for Product: " + self.product

def split_version_string(version_string):
    parameters = string.split(version_string, '.')
    if len(parameters) != 4:
        raise InvalidVersionException(version_string, '')

    return parameters[0], parameters[1], parameters[2], parameters[3]

def handle_uploaded_file(f):
    # TODO: moggi: get the path from the config
    file_path = os.path.join('/tmp/x', f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def create_database_entry(file, form):
    file_path = handle_uploaded_file(file)

    crash_id = uuid.uuid4()

    version = form.cleaned_data['Version']
    product = form.cleaned_data['ProductName']

    model_product = Product.objects.get(product_name=product)
    if not model_product:
        raise InvalidProductException(product)

    major, minor, micro, patch = split_version_string(version)
    try:
        model_version = Version.objects.get(product=model_product,
                major_version = major, minor_version = minor,
                micro_version = micro, patch_version = patch)
    except:
        traceback.print_exc()

    if not model_version:
        raise InvalidVersionException(version, product)

    new_crash = UploadedCrash(crash_path=file_path, crash_id=str(crash_id),
           version=model_version )
    new_crash.save()
    return crash_id

# TODO: moggi: move most of the code into own file
# keep the view file clean
@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST here')

    form = UploadFileForm(request.POST, request.FILES)

    file = request.FILES['upload_file_minidump']
    if file is None:
        return HttpResponseNotAllowed()

    if not form.is_valid():
        return HttpResponseNotAllowed()

    try:
        crash_id = str(create_database_entry(file, form))
    except (InvalidVersionException, InvalidProductException) as e:
        return HttpResponseServerError(str(e))

    return HttpResponseRedirect('Crash-ID=%s'%(crash_id))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
