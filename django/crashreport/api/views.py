# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from processor.models import ProcessedCrash, Signature, CrashCount, BugReport
from base.models import Version

@csrf_exempt
def api_crash_count(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('Only GET allowed')

    data = {'versions': {}}
    for v in Version.objects.all():
        version = v.str_without_product()
        crashes = ProcessedCrash.objects.get_crashes_for_version(version=version).count()
        data['versions'][version] = crashes
    return JsonResponse(data)

# Create your views here.
