# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count

from processor.models import ProcessedCrash, Signature
from django.contrib.staticfiles import finders

def main(request):
    return HttpResponse('main')

def crash_details(request, crash_id):

    crash = get_object_or_404(ProcessedCrash, crash_id=crash_id)
    modules = ['one module', 'another module']
    return render(request, 'stats/detail.html', {'crash': crash, 'modules':modules})

def signature(request, signature):
    signature_obj = get_object_or_404(Signature, signature=signature)
    crashes = signature_obj.processedcrash_set.all()
    return render(request, 'stats/signature.html', {'signature':signature_obj, 'crashes':crashes})


def top_crashes(request):
    return HttpResponse('top crashes')

class CrashByVersionData(object):
    def __init__(self, id):
        self.all = 0
        self.win = 0
        self.lin = 0
        self.id = id

def crashes_by_version(request, version):
    res = ProcessedCrash.objects.filter(crash_id__version__major_version=5, crash_id__version__minor_version=1).values('os_name', 'signature').annotate(Count('os_name'))
    data = {}
    for entry in res:
        signature = entry['signature']
        if not signature in data:
            data[signature] = CrashByVersionData(signature)
        count = entry['os_name__count']
        data[signature].all += count
        if entry['os_name'] == 'linux':
            data[signature].lin = count
        elif entry['os_name'] == 'windows':
            data[signature].win = count

    print(data.values())
    return render(request, 'stats/version.html', {'signatures':data.values()})

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
