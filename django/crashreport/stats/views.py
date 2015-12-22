# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from processor.models import ProcessedCrash, Signature, CrashCount
from crashsubmit.models import Version
from django.contrib.staticfiles import finders

import json, itertools

def generate_data_for_version(version, x_values, crashes):
    values = []
    for x in x_values:
        if x in crashes:
            values.append(crashes[x])
        else:
            values.append(None)
    data = {}
    data['data'] = ["1", "2", "3"]
    data['label'] = version
    data['fillColor'] = "rgba(220, 220, 220, 0.2)"
    data['strokeColor'] = "rgba(220, 220, 220, 1)"
    data['pointColor'] = "rgba(220, 220, 220, 1)"
    data['pointStrokeColor'] = "#fff"
    data['pointHighlightFill'] = "#fff"
    data['pointHighlightStroke'] = "#fff"
    data['data'] = values
    return data

def extract_x_values(crashes):
    return [str(s) for s in crashes.dates('date', 'day')]

def generate_chart_data():
    data = {}
    # TODO: moggi: how to handle dates without entries
    keys, values = CrashCount.objects.get_crash_count_processed()
    data['labels'] = keys
    data['datasets'] = []
    # TODO: moggi: make this generic
    data['datasets'].append(generate_data_for_version("5.1.0.0", keys, values['5.1.0.0']))
    return data

def main(request):
    featured = Version.objects.filter(featured=True)
    generated_chart_data = generate_chart_data()
    print(generated_chart_data)
    chart_data = json.dumps(generated_chart_data)
    print(chart_data)
    return render(request, 'stats/main.html', {'featured':featured, 'chart_data': chart_data})

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
