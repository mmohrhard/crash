# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseServerError

from crashsubmit import models as submit_model

from .models import ProcessedCrash

from processor import MinidumpProcessor

import subprocess

# Create your views here.

def process(request, crash_id):
    processor = MinidumpProcessor()
    processor.process(crash_id)

    return HttpResponse('CrashID=' + crash_id)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
