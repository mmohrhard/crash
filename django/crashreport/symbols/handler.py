# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from zipfile import ZipFile

from .models import SymbolsUpload, MissingSymbol

from django.utils import timezone
from django.conf import settings

import os

class SymbolsUploadHandler(object):

    def __init__(self):
        pass

    def process(self, data, path):
        zip_file = ZipFile(path)
        filename_list = zip_file.namelist()
        file_names = "\n".join(filename_list)
        zip_file.extractall(settings.SYMBOL_LOCATION)

        upload = SymbolsUpload()
        upload.files = file_names
        upload.comment = data['version'] + " " + data['platform']
        upload.upload_time = timezone.now()
        upload.system_symbols = data['system'] if 'system' in data else False;

        if upload.system_symbols is True:
            self._handle_missing_system_symbols(filename_list)
        upload.save()

    def _handle_missing_system_symbols(self, filenames):
        debug_ids = []
        for filename in filenames:
            try:
                debug_ids.append(os.path.split(os.path.split(filename)[0])[1])
            except:
                pass

        MissingSymbol.objects.filter(debug_id__in = debug_ids).delete()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
