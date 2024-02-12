# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, \
    HttpResponseBadRequest, Http404
from processor.models import ProcessedCrash, Signature, CrashCount, BugReport
from base.models import Version
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse

from django.views.generic import ListView
from django import forms
from django.db.models import Count
from django.core.paginator import Paginator

import json, itertools
import urllib
import logging

logger = logging.getLogger(__name__)

def generate_product_version_data():
    data = {}
    data['versions'] = Version.objects.order_by('-major_version', '-minor_version', '-micro_version', '-patch_version')
    return data

class ListViewBase(ListView):
    # this is an abstract class, each subclass needs to set at least the template_name and base_url

    def generate_product_version_data(self, data):
        data['versions'] = Version.objects.order_by('-major_version', '-minor_version', '-micro_version', '-patch_version')

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        self.generate_product_version_data(context)
        return context

    def post(self, request, *args, **kwargs):
        product = 'LibreOffice'
        version = '5.1.0.0'
        return HttpResponseRedirect(reverse(base_url, {'product': product, 'version': version}))

def main(request):
    featured_versions = Version.objects.filter(featured=True).order_by('-major_version', '-minor_version', '-micro_version', '-patch_version')
    data = generate_product_version_data()
    data['featured'] = featured_versions
    data['version'] = 'current'
    return render(request, 'stats/main.html', data)

def generate_bug_info(crash):
    comment_text = "This bug was filed from the crash reporting server and is br-%s.\n=========================================" % crash.crash_id
    signature = "[\"%s\"]" % crash.signature.signature
    return 'comment=%s&cf_crashreport=%s&short_desc=%s' % ( urllib.quote(comment_text, safe=''), urllib.quote(signature, safe=''), urllib.quote("Crash in: %s" % crash.signature.signature, safe='') )

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
    data['create_bug'] = generate_bug_info(crash)
    return render(request, 'stats/detail.html', data)

class BugNumberForm(forms.Form):
    bug_nr = forms.DecimalField(min_value=1)

def get_os_info(crashes):
    os_info = crashes.values('os_name').annotate(Count('os_name'))
    data = {}
    for os in os_info:
        data[os['os_name']] = os['os_name__count']

    return data

def get_cpu_architecture(crashes):
    cpu_architecture = crashes.values('cpu_architecture').annotate(Count('cpu_architecture'))

    data = {}
    for architecture in cpu_architecture:
        data[architecture['cpu_architecture']] = architecture['cpu_architecture__count']

    return data

def get_version_info(crashes):
    version_info = crashes.values('version').annotate(Count('version'))
    data = {}
    for version in version_info:
        data[str(Version.objects.get(id = version['version']))] = version['version__count']

    return data

class SignatureView(ListViewBase):
    template_name = 'stats/signature.html'
    context_object_name = 'crashes'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(SignatureView, self).get_context_data(**kwargs)
        signature_object = get_object_or_404(Signature, signature = self.kwargs['signature'])
        context['signature'] = signature_object
        context['bug_form'] = BugNumberForm()

        crashes = ProcessedCrash.objects.filter(signature = signature_object)
        context['os_info'] = get_os_info(crashes)
        context['cpu_info'] = get_cpu_architecture(crashes)
        context['version_info'] = get_version_info(crashes)
        return context

    def get_queryset(self):
        self.signature_obj = get_object_or_404(Signature, signature=self.kwargs['signature'])
        version = self.request.GET.get('version', None)
        crashes = self.signature_obj.processedcrash_set.all()
        if version is not None:
            version_filter_params = Version.get_filter_params(version, prefix='version__')
            crashes = crashes.filter(**version_filter_params)
        crashes = crashes.order_by("-upload_time")
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

        return HttpResponseRedirect(reverse('signature_details', args=[signature]) + '#bugs')

class TopCrashesView(ListViewBase):
    template_name = 'stats/version.html'
    context_object_name = 'signatures'

    def get_context_data(self, **kwargs):
        context = super(TopCrashesView, self).get_context_data(**kwargs)
        shown_crashes = 0
        for signature in context['signatures']:
            shown_crashes = shown_crashes + signature.all
        context['shown_crashes'] = shown_crashes
        limit = int(self.request.GET.get('limit', 50))
        context['limit'] = limit
        days = int(self.request.GET.get('days', 7))
        context['days'] = days
        if 'version' in self.kwargs:
            context['version'] = self.kwargs['version']
        else:
            context['version'] = self.request.GET.get('version', None)
        context['all_crashes'] = ProcessedCrash.objects.get_crashes_for_version(context['version']).count()
        return context

    def get_queryset(self):
        days = int(self.request.GET.get('days', 7))
        limit = int(self.request.GET.get('limit', 50))
        if 'version' in self.kwargs:
            version = self.kwargs['version']
        else:
            version = self.request.GET.get('version', None)
        top_crash = ProcessedCrash.objects.get_top_crashes(time=days, limit=limit, version=version)
        return top_crash

def crash_search(request):
    if request.method == 'POST' and request.POST['search_id']:
        crash_id = (request.POST['search_id']).strip()
        return redirect('crash_details', crash_id=crash_id)
    raise Http404()

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
