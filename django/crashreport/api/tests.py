# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.utils import timezone

from base.models import Version
from processor.models import ProcessedCrash, Signature

# Create your tests here.

class ApiCrashCountTest(TestCase):

    def setUp(self):
        self.version1 = Version.objects.create(
                major_version=1, minor_version=2, micro_version=3, patch_version=4)
        self.signature = Signature.objects.create(signature='cde', first_observed= timezone.now(), last_observed = timezone.now())

    def test_post(self):
        c = Client()
        response = c.post('/api/get/crash-count')
        self.assertEqual(response.status_code, 405)

    def test_simple(self):
        ProcessedCrash.objects.create(crash_id='abc', version = self.version1,
                os_name = 'Linux', signature = self.signature, upload_time = timezone.now())
        c = Client()
        response = c.get('/api/get/crash-count')
        print(response.content)
