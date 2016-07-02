# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import UploadedCrash

from processor.signals import do_process_uploaded_crash

import logging
import os

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UploadedCrash)
def process_uploaded_crash(sender, instance, **kwargs):
    do_process_uploaded_crash.spool(crash_id = instance.crash_id)

@receiver(pre_delete, sender=UploadedCrash)
def process_deleted_crash(sender, instance, **kwargs):
    try:
        os.remove(instance.crash_path)
    except:
        pass

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
