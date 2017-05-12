# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from processor.models import ProcessedCrash, Signature, CrashCount, BugReport
from base.models import Version

@csrf_exempt
def api_crash_count(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed('Only GET allowed')

    version_info = ProcessedCrash.objects.all().values('version').annotate(Count('version'))
    data = {}
    for version in version_info:
        data[Version.objects.get(id = version['version']).str_without_product()] = version['version__count']

    data = {'versions': data}
    return JsonResponse(data)

# Create your views here.
