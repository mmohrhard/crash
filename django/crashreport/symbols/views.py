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

import os
import logging

logger = logging.getLogger(__name__)

class UploadSymbolsForm(forms.Form):
    symbols = forms.FileField()
    version = forms.CharField()
    platform = forms.CharField()

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

def add_missing_symbols(missing_symbols, module_list):
    modules = module_list.splitlines()
    # Module|actxprxy.dll|6.1.7601.17514|ActXPrxy.pdb|C674D3ABFBB34B75BC59063E6B68ABA12|0x6a710000|0x6a75dfff|0
    for module in modules:
        module_entries = module.split('|')
        if len(module_entries) < 5:
            continue

        symbol_file = module_entries[3]
        debug_id = module_entries[4]

        dir_path = os.path.join(settings.SYMBOL_LOCATION, symbol_file)
        if not os.path.exists(dir_path):
            missing_symbols.add(symbol_file + "," + debug_id)
            continue

        symbol_file_dir = os.path.join(settings.SYMBOL_LOCATION, debug_id)

        if not os.path.exists(symbol_file_dir):
            missing_symbols.add(symbol_file + "," + debug_id)

@csrf_exempt
@login_required
def find_missing_symbols(request):

    if request.method != 'GET':
        return HttpResponseNotAllowed("Only GET here")

    crashes = ProcessedCrash.objects.get_crashes_for_day(None)
    missing_symbols = []
    for crash in crashes:
        add_missing_symbols(missing_symbols, crash.modules)

    return HttpResponse("\n".join(missing_symbols))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
