# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.conf.urls import url

from . import views

urlpatterns = [
        url(r'missing$', views.find_missing_symbols, name='missing_symbols'),
        url(r'^$', views.upload_symbols, name='symbols'),
        ]

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
