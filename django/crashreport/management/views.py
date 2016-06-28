# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django import forms
from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from processor.models import Signature, BugReport

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

    crash_object = get_object_or_404(Signature, signature = form.cleaned_data['signature'])

    bug_report = BugReport.objects.get_or_create(bug_nr = int(form.cleaned_data['bug_nr']))

    crash_object.bugs.add(bug_report[0])

    return HttpResponse('Ok')

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
