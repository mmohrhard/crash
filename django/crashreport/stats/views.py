# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from processor.models import ProcessedCrash, Signature, CrashCount
from base.models import Version, Product
from django.contrib.staticfiles import finders

import json, itertools

# TODO: moggi: maybe switch to a class based view
def generate_product_version_data():
    res = {}
    res['products'] = Product.objects.all()
    # TODO: moggi: only export current versions
    res['versions'] = Version.objects.all()
    return res

def generate_data_for_version(version, x_values, crashes):
    values = []
    for x in x_values:
        if x in crashes:
            values.append(crashes[x])
        else:
            values.append(None)
    data = {}
    data['label'] = version
    # TODO: moggi: generate colors for each series
    data['fillColor'] = "rgba(220, 220, 220, 0.2)"
    data['strokeColor'] = "rgba(220, 220, 220, 1)"
    data['pointColor'] = "rgba(220, 220, 220, 1)"
    data['pointStrokeColor'] = "#fff"
    data['pointHighlightFill'] = "#fff"
    data['pointHighlightStroke'] = "#fff"
    data['data'] = values
    return data

def generate_chart_data(featured):
    data = {}
    # TODO: moggi: how to handle dates without entries
    keys, values = CrashCount.objects.get_crash_count_processed(versions=featured)
    data['labels'] = keys
    data['datasets'] = []
    for version in values.keys():
        data['datasets'].append(generate_data_for_version(version, keys, values[version]))
    return data

def main(request):
    featured = Version.objects.filter(featured=True)
    generated_chart_data = generate_chart_data(featured)
    chart_data = json.dumps(generated_chart_data)
    data = generate_product_version_data()
    data['featured'] = featured
    data['chart_data'] = chart_data
    return render(request, 'stats/main.html', data)

def crash_details(request, crash_id):
    crash = get_object_or_404(ProcessedCrash, crash_id=crash_id)
    modules = crash.get_split_module_list()
    data = generate_product_version_data()
    data['crash'] = crash
    data['modules'] = modules
    return render(request, 'stats/detail.html', data)

def signature(request, signature):
    signature_obj = get_object_or_404(Signature, signature=signature)
    crashes = signature_obj.processedcrash_set.all()
    data = generate_product_version_data()
    data['signature'] = signature_obj
    data['crashes'] = crashes
    return render(request, 'stats/signature.html', data)


def handle_parameter_or_default(data, param_name, default):
    if param_name in data:
        return data[param_name]

    return default

def top_crashes(request):
    days = int(handle_parameter_or_default(request.GET, 'days', 1))
    limit = int(handle_parameter_or_default(request.GET, 'limit', 10))
    version = handle_parameter_or_default(request.GET, 'version', None)
    top_crash = ProcessedCrash.objects.get_top_crashes(time=days, limit=limit, version=version)
    data = generate_product_version_data()
    data['signatures'] = top_crash
    return render(request, 'stats/version.html', data)

def crashes_by_version(request, version):
    # TODO: moggi: remove hard coded version entry
    top_crash = ProcessedCrash.objects.get_top_crashes(version='5.1', limit=10)
    data = generate_product_version_data()
    data['signatures'] = top_crash
    data['version'] = version
    return render(request, 'stats/version.html', data)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
