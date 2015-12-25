# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from zipfile import ZipFile

from .models import SymbolsUpload

from django.utils import timezone

class SymbolsUploadHandler(object):

    # TODO: moggi: get symbol location from configuration
    symbol_location = "/tmp/symbols/"

    def __init__(self):
        pass

    def process(self, data, path):
        print(data)
        zip_file = ZipFile(path)
        file_names = "\n".join(zip_file.namelist())
        zip_file.extractall(SymbolsUploadHandler.symbol_location)

        upload = SymbolsUpload()
        upload.files = file_names
        upload.comment = data['comment']
        upload.upload_time = timezone.now()
        upload.save()


# vim:set shiftwidth=4 softtabstop=4 expandtab: */
