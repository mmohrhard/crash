# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django import forms
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

from .models import UploadedCrash
from base.models import Version

import os, uuid
import string
import json

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError

class UploadFileForm(forms.Form):
    upload_file_minidump = forms.FileField()

    # These two attributes are deprecated
    AdapterDeviceId = forms.CharField(required = False)
    AdapterVendorId = forms.CharField(required = False)

    # Only use the new AdditionalData field which would require json data
    AdditionalData = forms.CharField(required = False)
    Version = forms.CharField()

class InvalidVersionException(Exception):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return "Invalid Version: " + self.version

def handle_uploaded_file(f):
    tmp_upload_path = settings.TEMP_UPLOAD_DIR
    file_path = os.path.join(tmp_upload_path, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path


def create_database_entry(file, form):
    version = form.cleaned_data['Version']

    try:
        model_versions = Version.objects.get_by_version_string(version)
        if len(model_versions) != 1:
            raise InvalidVersionException(str(model_versions))

        model_version = model_versions[0]
    except:
        raise InvalidVersionException(version)

    if not model_version:
        raise InvalidVersionException(version)

    file_path = handle_uploaded_file(file)

    crash_id = uuid.uuid4()

    json_data = {}

    try:
        if form.cleaned_data['AdditionalData'] != "":
            json_data = json.loads(form.cleaned_data['AdditionalData'])
    except:
        pass

    try:
        if form.cleaned_data['AdapterDeviceId'] != "":
            json_data['Grahic Device ID'] = form.cleaned_data['AdapterDeviceId']
        if form.cleaned_data["AdapterVendorId"] != "":
            json_data['Graphic Vendor ID'] = form.cleaned_data['AdapterVendorId']
    except:
        pass

    new_crash = UploadedCrash(crash_path=file_path, crash_id=str(crash_id),
           version=model_version, additional_data = json.dumps(json_data) )
    new_crash.save()
    return crash_id

# TODO: moggi: move most of the code into own file
# keep the view file clean
@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST here')

    form = UploadFileForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponseBadRequest()

    file = request.FILES['upload_file_minidump']

    try:
        crash_id = str(create_database_entry(file, form))
    except (InvalidVersionException) as e:
        return HttpResponseServerError(str(e))

    return HttpResponse('Crash-ID=%s'%(crash_id))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
