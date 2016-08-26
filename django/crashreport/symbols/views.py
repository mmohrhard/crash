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

def create_symbols_entry(module_entries):
    symbol_file = module_entries[3]
    debug_id = module_entries[4]

    entry = symbol_file + "," + debug_id

    if len(module_entries) >= 9:
        entry = entry + "," + module_entries[1] + "," + module_entries[8]

    return entry

def add_missing_symbols(missing_symbols, module_list, symbol_ids):
    modules = module_list.splitlines()
    # Module|{code_name}|6.1.7601.17514|{debug_name}|{debug_id}|0x6a710000|0x6a75dfff|{main?}|{Code_id}
    for module in modules:
        module_entries = module.split('|')
        if len(module_entries) < 5:
            continue

        symbol_file = module_entries[3]
        debug_id = module_entries[4]

        # this is not a code module
        if debug_id == "000000000000000000000000000000000":
            continue

        if symbol_file not in symbol_ids:
            missing_symbols.add(create_symbols_entry(module_entries))
            continue

        debug_ids = symbol_ids.get(symbol_file)

        if debug_id not in debug_ids:
            missing_symbols.add(create_symbols_entry(module_entries))

def get_all_existing_symbols():
    libs = set(os.listdir(settings.SYMBOL_LOCATION))
    symbol_ids = {}
    for lib in libs:
        symbol_ids[lib] = set(os.listdir(os.path.join(settings.SYMBOL_LOCATION, lib)))

    return symbol_ids

@csrf_exempt
@login_required
def find_missing_symbols(request):

    if request.method != 'GET':
        return HttpResponseNotAllowed("Only GET here")

    symbold_ids = get_all_existing_symbols()

    crashes = ProcessedCrash.objects.get_crashes_for_day(None, None)
    missing_symbols = set()
    for crash in crashes:
        add_missing_symbols(missing_symbols, crash.modules, symbol_ids)

    return HttpResponse("\n".join(missing_symbols))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
