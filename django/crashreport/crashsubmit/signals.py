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

from uwsgidecoratorsfallback import cron

import logging
import os
import datetime

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

@cron(1, 1, -1, -1, -1)
def remove_old_uploads(args):
    delete_date = datetime.date.today() - datetime.timedelta(days=30)
    UploadedCrash.objects.filter(upload_time__date__lte=delete_date).delete()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
