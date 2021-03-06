# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'add-bug$', views.add_bug_report),
        url(r'set-bug-status$', views.set_bug_status),
        url(r'create-daily-stats$', views.create_daily_stats),
        url(r'add-version/(?P<version>.+)$', views.add_version),
        ]

# vim:set shiftwidth=4 softtabstop=4 expandtab: */

