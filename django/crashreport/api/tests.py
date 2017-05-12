# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client

from base.models import Version

# Create your tests here.

class ApiCrashCountTest(TestCase):

    def setUp(self):
        self.version1 = Version.objects.create(
                major_version=1, minor_version=2, micro_version=3, patch_version=4)

    def test_post(self):
        c = Client()
        response = c.post('/api/get/crash-count/')
        self.assertEqual(response.status_code, 404)
