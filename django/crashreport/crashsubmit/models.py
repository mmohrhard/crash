# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import unicode_literals

from django.db import models

from base.models import Version

class UploadedCrash(models.Model):
    # TODO: moggi: change to UUIDField
    crash_id = models.CharField(max_length=50,
            unique=True)
    # TODO: moggi: change to FilePathField
    crash_path = models.CharField(max_length=200, help_text='The path to the original crash report on the file system.')
    upload_time = models.DateTimeField(auto_now_add=True)
    version = models.ForeignKey(Version)
    device_id = models.CharField(max_length=100,
            null=True)
    vendor_id = models.CharField(max_length=100,
            null=True)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
