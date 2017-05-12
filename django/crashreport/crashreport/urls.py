"""crashreport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls)
"""

# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#



from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

import debug_toolbar

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/stats/')),
    url(r'^api/', include('api.urls')),
    url(r'^submit/', include('crashsubmit.urls')),
    url(r'^process/', include('processor.urls')),
    url(r'^symbols/', include('symbols.urls')),
    url(r'^upload/', include('symbols.urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'^management/', include('management.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^debug/', include(debug_toolbar.urls)),
]

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
