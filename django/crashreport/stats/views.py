# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from processor.models import ProcessedCrash
from django.contrib.staticfiles import finders

def main(request):
    return HttpResponse('main')

def crash_details(request, crash_id):

    crash = get_object_or_404(ProcessedCrash, crash_id=crash_id)
    modules = ['one module', 'another module']
    return render(request, 'stats/detail.html', {'crash': crash, 'modules':modules})

def top_crashes(request):
    return HttpResponse('top crashes')

def crashes_by_version(request, version):
    return HttpResponse('crashes for version: %s' % (version))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
