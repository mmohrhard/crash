# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from .models import SymbolsUpload, MissingSymbol, MissingSymbolConfig

from processor.models import ProcessedCrash

from uwsgidecoratorsfallback import cron

import logging
import os
import subprocess
import sys
import datetime

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

@receiver(post_save, sender=SymbolsUpload)
def process_uploaded_symbols(sender, instance, **kwargs):
    if instance.system_symbols:
        return

    logger.info('processing symbols for: "%s"' % (instance.comment))
    symbol_location = settings.SYMBOL_LOCATION
    for symbol_file in instance.files.splitlines():
        symbol_path = os.path.join(symbol_location, symbol_file)
        try:
            command = ["python", os.path.abspath(settings.SYMBOL_PROCESSING), symbol_path]
            subprocess.check_call(command)
        except OSError as e:
            logger.warn("error while processing %s: %s" % (symbol_file,  e.strerror))
        except:
            logger.warn("error while processing %s: %s" % (symbol_file,  str(sys.exc_info()[0])))

def create_symbols_entry(module_entries):
    data = { 'symbol_file': module_entries[3],
            'debug_id': module_entries[4],
            'code_name':'',
            'code_id':''}

    if len(module_entries) >= 9:
        data['code_name'] = module_entries[1]
        data['code_id'] = module_entries[8]

    if MissingSymbol.objects.filter(**data).exists():
        return

    MissingSymbol.objects.create(**data)

def add_missing_symbols(module_list):
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

        dir_path = os.path.join(settings.SYMBOL_LOCATION, symbol_file)
        if not os.path.exists(dir_path):
            create_symbols_entry(module_entries)
            continue

        symbol_file_dir = os.path.join(dir_path, debug_id)

        if not os.path.exists(symbol_file_dir):
            create_symbols_entry(module_entries)

@cron(-1, -1, -1, -1, -1)
def collect_missing_symbols(args):
    print("collect_missing_symbols")
    configs = MissingSymbolConfig.objects.all()
    date = datetime.datetime(2010, 1, 1)
    if configs.count() > 0:
        date = configs[0].last_time
        configs.delete()

    MissingSymbolConfig.objects.create(last_time = timezone.now())
    crashes = ProcessedCrash.objects.filter(process_time__gte=date).only('modules')
    print(crashes.count())
    for crash in crashes:
        add_missing_symbols(crash.modules)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
