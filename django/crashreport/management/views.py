# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import HttpResponseNotAllowed
from django import forms
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from base.models import Version
from processor.models import Signature, BugReport, ProcessedCrash, CrashCount

from django.utils import timezone

from datetime import timedelta

import logging

logger = logging.getLogger(__name__)

class AddBugForm(forms.Form):
    signature = forms.CharField(max_length = 255)
    bug_nr = forms.IntegerField(min_value=1)

@login_required
@csrf_exempt
def add_bug_report(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST allowed.')

    form = AddBugForm(request.POST, request.FILES)
    if not form.is_valid():
        logger.warning("form is invalid with error: " + str(form.errors))
        return HttpResponseBadRequest()

    signatures = Signature.objects.filter(signature = form.cleaned_data['signature'])
    if signatures.count() == 0:
        processed_crash = get_object_or_404(ProcessedCrash, crash_id = form.cleaned_data['signature'])
        signature_object = processed_crash.signature
    else:
        signature_object = signatures[0]

    bug_report = BugReport.objects.get_or_create(bug_nr = int(form.cleaned_data['bug_nr']))

    signature_object.bugs.add(bug_report[0])

    return HttpResponse('Ok')

class SetBugStatusForm(forms.Form):
    bug_nr = forms.IntegerField(min_value=1)
    fixed = forms.BooleanField(required=False)

@login_required
@csrf_exempt
def set_bug_status(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST allowed.')

    form = SetBugStatusForm(request.POST, request.FILES)
    if not form.is_valid():
        logger.warning("form is invalid with error: " + str(form.errors))
        return HttpResponseBadRequest()

    bug_report = get_object_or_404(BugReport, bug_nr = int(form.cleaned_data['bug_nr']))

    bug_report.fixed = form.cleaned_data['fixed']
    bug_report.save()

    return HttpResponse('Ok')

@login_required
@csrf_exempt
def create_daily_stats(request):
    featured_versions = Version.objects.filter(featured=True)
    for day in range(1, 7):
        for version in featured_versions:
            date = timezone.now().today() - timedelta(days=day)
            crash_count = CrashCount.objects.get_or_create(version=version, date = date)
            if crash_count[1] is True:
                crashes = ProcessedCrash.objects.get_crashes_for_day(date, version)
                crash_count[0].count = len(crashes)
                crash_count[0].save()
    return HttpResponse('OK')

@login_required
@csrf_exempt
def add_version(request, version):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST allowed')

    parsed = Version.get_filter_params(version)
    if len(parsed) != 4:
        return HttpResponseBadRequest('Bad version string')

    Version.objects.create_from_string(version)
    return HttpResponse('Version added')

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
