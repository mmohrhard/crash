# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'crash_details/(?P<crash_id>.+)$', views.crash_details, name='crash_details'),
        url(r'top_crashes$', views.top_crashes),
        url(r'version/(?P<version>.+)$', views.crashes_by_version),
        url(r'signature/(?P<signature>.+)$', views.signature, name='signature_details'),
        url(r'', views.main),
        ]



# vim:set shiftwidth=4 softtabstop=4 expandtab: */
