# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
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

@csrf_exempt
def api_chart_data(request, days):
    """API generates the chart data for chart."""

    if request.method != 'GET':
        return HttpResponseNotAllowed('Only GET allowed')

    days = int(days)
    valid_days = [1, 3, 7, 14, 28]
    if days not in valid_days:
        return HttpResponseBadRequest('Days are not valid.')

    featured_versions = Version.objects.filter(featured=True)
    generated_chart_data = generate_chart_data(featured_versions, days)
    chart_data = generated_chart_data
    return JsonResponse(chart_data)

class ChartColorMap(object):

    color_list = [ "rgba(255, 255, 171, {0})",
                "rgba(190, 186, 218, {0})", "rgba(251, 128, 114, {0})", "rgba(128, 177, 211, {0})",
                "rgba(253, 180, 98, {0})", "rgba(179, 222, 105, {0})", "rgba(252, 205, 229, {0})",
                "rgba(217, 217, 217, {0})", "rgba(188, 128, 189, {0})", "rgba(141, 211, 199, {0})" ]

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
    data['borderWidth'] = 2.5
    data['pointBorderWidth'] = 1.5
    data['pointRadius'] = 4
    data['fill'] = True

    color_with_alpha = ChartColorMap.get_color_by_index(id, 0.2)
    color = ChartColorMap.get_color_by_index(id, 1)
    data['backgroundColor'] = color_with_alpha
    data['borderColor'] = color
    data['pointBackgroundColor'] = color
    data['pointBorderColor'] = "#fff"
    data['pointHoverBackgroundColor'] = "#fff"
    data['pointHoverBorderColor'] = "#fff"

    data['data'] = values
    return data

def generate_chart_data(featured_versions, days):
    data = {}
    keys, values = CrashCount.objects.get_crash_count_processed(versions=featured_versions, time=days + 1)
    data['labels'] = keys
    data['datasets'] = []
    for id, version in enumerate(values.keys()):
        data['datasets'].append(generate_data_for_version(id, version, keys, values[version]))
    return data
