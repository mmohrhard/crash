# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'get/crash-count$', views.api_crash_count, name='api_crash_count'),
        url(r'get/chart-data/([1-9]{1,2})$', views.api_chart_data, name='api_chart_data'),
        ]

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
