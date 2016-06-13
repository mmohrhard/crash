# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from processor.models import ProcessedCrash, Signature, CrashCount, BugReport
from base.models import Version
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse

from django.views.generic import ListView
from django import forms

import json, itertools
import logging

logger = logging.getLogger(__name__)

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

class ChartColorMap(object):

    color_list = [ "rgba(141, 211, 199, {0})", "rgba(255, 255, 171, {0})",
                "rgba(190, 186, 218, {0})", "rgba(251, 128, 114, {0})", "rgba(128, 177, 211, {0})",
                "rgba(253, 180, 98, {0})", "rgba(179, 222, 105, {0})", "rgba(252, 205, 229, {0})",
                "rgba(217, 217, 217, {0})", "rgba(188, 128, 189, {0})" ]

    @classmethod
    def get_color_by_index(cls, index, alpha = 1):
        return cls.color_list[index].format(alpha)

def generate_data_for_version(id, version, x_values, crashes):
    values = []
    for x in x_values:
        if x in crashes:
            values.append(crashes[x])
        else:
            values.append(None)

    data = {}
    data['label'] = version

    color = ChartColorMap.get_color_by_index(id, 1)
    color_with_alpha = ChartColorMap.get_color_by_index(id, 0.2)
    data['fillColor'] = color_with_alpha
    data['strokeColor'] = color
    data['pointColor'] = color
    data['pointStrokeColor'] = "#fff"
    data['pointHighlightFill'] = "#fff"
    data['pointHighlightStroke'] = "#fff"

    data['data'] = values
    return data

def generate_chart_data(featured_versions):
    data = {}
    # TODO: moggi: how to handle dates without entries
    keys, values = CrashCount.objects.get_crash_count_processed(versions=featured_versions)
    data['labels'] = keys
    data['datasets'] = []
    for id, version in enumerate(values.keys()):
        data['datasets'].append(generate_data_for_version(id, version, keys, values[version]))
    return data

def main(request):
    featured_versions = Version.objects.filter(featured=True)
    generated_chart_data = generate_chart_data(featured_versions)
    # TODO: moggi: load the chart data through a rest api dynamically
    chart_data = json.dumps(generated_chart_data)
    data = generate_product_version_data()
    data['featured'] = featured_versions
    data['chart_data'] = chart_data
    data['version'] = 'current'
    return render(request, 'stats/main.html', data)

def crash_details(request, crash_id):
    crash = get_object_or_404(ProcessedCrash, crash_id=crash_id)
    modules = crash.get_split_module_list()
    data = generate_product_version_data()
    data['crash'] = crash
    data['additional_data'] = json.loads(crash.additional_data)
    data['modules'] = modules
    data['crashing_thread'] = {'frames': json.loads(crash.crashing_thread)}
    data['threads'] = json.loads(crash.threads)
    data['version'] = 'current'
    return render(request, 'stats/detail.html', data)

class BugNumberForm(forms.Form):
    bug_nr = forms.DecimalField(min_value=1)

class SignatureView(ListViewBase):
    template_name = 'stats/signature.html'
    context_object_name = 'crashes'

    def get_context_data(self, **kwargs):
        context = super(SignatureView, self).get_context_data(**kwargs)
        context['signature'] = get_object_or_404(Signature, signature=self.kwargs['signature'])
        context['bug_form'] = BugNumberForm()
        return context

    def get_queryset(self):
        self.signature_obj = get_object_or_404(Signature, signature=self.kwargs['signature'])
        crashes = self.signature_obj.processedcrash_set.all()
        return crashes

    def post(self, request, *args, **kwargs):

        bug_nr_form = BugNumberForm(request.POST)
        if not bug_nr_form.is_valid():
            logger.warning("invalid bug number form data: " + str(bug_nr_form.errors))
            return HttpResponseBadRequest()

        bug_nr = bug_nr_form.cleaned_data['bug_nr']
        signature = kwargs['signature']
        bug = BugReport.objects.get_or_create(bug_nr=bug_nr)
        sig = Signature.objects.get(signature=signature)
        sig.bugs.add(bug[0])

        return HttpResponseRedirect(reverse('signature_details', args=[signature]))

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
        else:
            context['version'] = handle_parameter_or_default(self.request.GET, 'version', None)
        return context

    def get_queryset(self):
        days = int(handle_parameter_or_default(self.request.GET, 'days', 7))
        limit = int(handle_parameter_or_default(self.request.GET, 'limit', 50))
        if 'version' in self.kwargs:
            version = self.kwargs['version']
        else:
            version = handle_parameter_or_default(self.request.GET, 'version', None)
        top_crash = ProcessedCrash.objects.get_top_crashes(time=days, limit=limit, version=version)
        return top_crash

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
