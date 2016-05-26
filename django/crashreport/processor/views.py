# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from processor import MinidumpProcessor

from crashsubmit import models
from .models import ProcessedCrash

@login_required
def process_all(request):
    # move that to a Manager
    processed_crashes = ProcessedCrash.objects.values_list('crash_id')
    crashes = models.UploadedCrash.objects.exclude(crash_id__in=processed_crashes)
    done = []
    for crash in crashes:
        procescor = MinidumpProcessor()
        procescor.process(crash.crash_id)
        done.append(crash.crash_id)
    return HttpResponse("\n".join(done))

@login_required
def process(request, crash_id):
    processor = MinidumpProcessor()
    processor.process(crash_id)

    return HttpResponse('CrashID=' + crash_id)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
