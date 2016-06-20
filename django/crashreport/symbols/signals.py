# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings

from .models import SymbolsUpload

import logging
import os

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=SymbolsUpload)
def process_deleted_symbols(sender, instance, **kwargs):
    logger.info('deleting symbols for: "%s"' % (instance.comment))
    symbol_location = settings.SYMBOL_LOCATION
    for symbol_file in instance.files.splitlines():
        symbol_path = os.path.join(symbol_location, symbol_file)
        try:
            os.remove(symbol_path)
        except:
            pass

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
