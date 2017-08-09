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

class ApiChartDataTest(TestCase):

    valid_days = [1, 3, 7, 14, 28]
    invalid_days = [4, 8, 16, 25, 55]

    def test_valid_days_get(self):
        """
        Tests server response with a GET request and valid days
        """
        c = Client()

        for i in self.valid_days:
            response = c.get('/api/get/chart-data/{}'.format(i))
            self.assertEqual(response.status_code, 200)

    def test_invalid_days_get(self):
        """
        Tests server response with a GET request and invalid days
        """
        c = Client()

        for i in self.invalid_days:
            response = c.get('/api/get/chart-data/{}'.format(i))
            self.assertEqual(response.status_code, 400)

    def test_post(self):
        """
        Tests server response with a POST request and valid days
        """
        c = Client()

        for i in self.valid_days:
            response = c.post('/api/get/chart-data/{}'.format(i))
            self.assertEqual(response.status_code, 405)
            print(response.content)
