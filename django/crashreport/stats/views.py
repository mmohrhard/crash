# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from processor.models import ProcessedCrash, Signature
from django.contrib.staticfiles import finders

def main(request):
    return HttpResponse('main')

def crash_details(request, crash_id):

    crash = get_object_or_404(ProcessedCrash, crash_id=crash_id)
    modules = crash.get_split_module_list()
    return render(request, 'stats/detail.html', {'crash': crash, 'modules':modules})

def signature(request, signature):
    signature_obj = get_object_or_404(Signature, signature=signature)
    crashes = signature_obj.processedcrash_set.all()
    return render(request, 'stats/signature.html', {'signature':signature_obj, 'crashes':crashes})


def handle_parameter_or_default(data, param_name, default):
    if param_name in data:
        return data[param_name]

    return default

def top_crashes(request):
    days = int(handle_parameter_or_default(request.GET, 'days', 1))
    limit = int(handle_parameter_or_default(request.GET, 'limit', 10))
    version = handle_parameter_or_default(request.GET, 'version', None)
    data = ProcessedCrash.objects.get_top_crashes(time=days, limit=limit, version=version)
    return render(request, 'stats/version.html', {'signatures':data})

def crashes_by_version(request, version):
    data = ProcessedCrash.objects.get_top_crashes(version='5.1', limit=10)
    return render(request, 'stats/version.html', {'signatures':data})

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
