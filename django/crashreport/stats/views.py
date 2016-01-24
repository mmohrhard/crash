# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect

from processor.models import ProcessedCrash, Signature, CrashCount
from base.models import Version
from django.contrib.staticfiles import finders

from django.views.generic import ListView

import json, itertools

def generate_product_version_data():
    data = {}
    data['versions'] = Version.objects.all()
    return data

class ListViewBase(ListView):
    # this is an abstract class, each subclass needs to set at least the template_name and base_url

    def generate_product_version_data(self, data):
        data['versions'] = Version.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.generate_product_version_data(context)
        return context

    def post(self, request, *args, **kwargs):
        product = 'LibreOffice'
        version = '5.1.0.0'
        return HttpResponseRedirect(reverse(base_url, {'product': product, 'version': version}))

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

class SignatureView(ListViewBase):
    template_name = 'stats/signature.html'
    context_object_name = 'crashes'

    def get_context_data(self, **kwargs):
        context = super(SignatureView, self).get_context_data(**kwargs)
        context['signature'] = self.kwargs['signature']
        return context

    def get_queryset(self):
        self.signature_obj = get_object_or_404(Signature, signature=self.kwargs['signature'])
        crashes = self.signature_obj.processedcrash_set.all()
        return crashes

def handle_parameter_or_default(data, param_name, default):
    if param_name in data:
        return data[param_name]

    return default

class TopCrashesView(ListViewBase):
    template_name = 'stats/version.html'
    context_object_name = 'signatures'

    def get_context_data(self, **kwargs):
        context = super(TopCrashesView, self).get_context_data(**kwargs)
        if 'version' in self.kwargs:
            context['version'] = self.kwargs['version']
        return context

    def get_queryset(self):
        days = int(handle_parameter_or_default(self.request.GET, 'days', 1))
        limit = int(handle_parameter_or_default(self.request.GET, 'limit', 10))
        print(self.kwargs)
        if 'version' in self.kwargs:
            version = self.kwargs['version']
        else:
            version = handle_parameter_or_default(self.request.GET, 'version', None)
        top_crash = ProcessedCrash.objects.get_top_crashes(time=days, limit=limit, version=version)
        return top_crash

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
