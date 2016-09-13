# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django import forms
from django.http import HttpResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .handler import SymbolsUploadHandler

from processor.models import ProcessedCrash

from .models import MissingSymbol

import os
import logging

logger = logging.getLogger(__name__)

class UploadSymbolsForm(forms.Form):
    symbols = forms.FileField()
    version = forms.CharField()
    platform = forms.CharField()
    system = forms.BooleanField(required=False)

def handle_uploaded_file(f):
    file_path = os.path.join(settings.SYMBOL_UPLOAD_DIR, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path

@csrf_exempt
@login_required
def upload_symbols(request):

    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST here')

    form = UploadSymbolsForm(request.POST, request.FILES)

    if not form.is_valid():
        logger.error("form is invalid with error: " + str(form.errors))
        return HttpResponseNotAllowed('Invalid data')

    path = handle_uploaded_file(request.FILES['symbols'])
    upload = SymbolsUploadHandler()
    upload.process(form.cleaned_data, path)

    return HttpResponse("Success")

@login_required
def get_missing_symbols(request):

    if request.method != 'GET':
        return HttpResponseNotAllowed("Only GET here")

    missing_symbols = MissingSymbol.objects.all()

    symbol_list = [ symbol.symbol_file + ',' + symbol.debug_id + ',' + symbol.code_name + ',' + symbol.code_id for symbol in missing_symbols]

    return HttpResponse("\n".join(symbol_list))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
