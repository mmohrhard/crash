# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.utils import timezone

from datetime import timedelta

from processor import MinidumpProcessor

from .models import ProcessedCrash, CrashCount
from base.models import Version

import logging

logger = logging.getLogger(__name__)

@login_required
def process_all(request):
    crashes = ProcessedCrash.objects.get_crashes_to_process()
    done = []
    for crash in crashes:
        procescor = MinidumpProcessor()
        procescor.process(crash.crash_id)
        done.append(crash.crash_id)
        logger.info('processed: ' + crash.crash_id)
    return HttpResponse("\n".join(done))

@login_required
def process(request, crash_id):
    processor = MinidumpProcessor()
    processor.process(crash_id)

    logger.info('processed: ' + crash.crash_id)
    return HttpResponse('CrashID=' + crash_id)

@login_required
def create_stats(request):
    featured_versions = Version.objects.filter(featured=True)
    print(featured_versions)
    for day in range(1, 7):
        for version in featured_versions:
            date = timezone.now().today() - timedelta(days=day)
            crash_count = CrashCount.objects.get_or_create(version=version, date = date)
            if crash_count[1] is True:
                crashes = ProcessedCrash.objects.get_crashes_for_day(date, version)
                crash_count[0].count = len(crashes)
                crash_count[0].save()
    return HttpResponse('OK')

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
