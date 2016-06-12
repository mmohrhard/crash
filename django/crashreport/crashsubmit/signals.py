# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.db.models.signals import post_save
from django.dispatch import receiver

from processor.processor import MinidumpProcessor
from .models import UploadedCrash

from uwsgidecoratorsfallback import spool

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UploadedCrash)
def process_uploaded_crash(sender, **kwargs):
    do_process_uploaded_crash.spool(crash_id = kwargs['instance'].crash_id)

@spool
def do_process_uploaded_crash(env):
    minproc = MinidumpProcessor()
    minproc.process(env['crash_id'])
    logger.info('processed: %s' % (env['crash_id']))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
