from django.test import TestCase

from .models import CrashCount

from base.models import Version, Product

import datetime
from django.utils import timezone

def get_date_n_days_ago(num_days):
    return datetime.date.fromordinal(datetime.date.today().toordinal() - num_days)

class CrashCountManagerTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(product_name="Product")
        self.version1 = Version.objects.create(product=self.product,
                major_version=1, minor_version=2, micro_version=3, patch_version=4)
        self.version2 = Version.objects.create(product=self.product,
                major_version=2, minor_version=2, micro_version=3, patch_version=4)

        yesterday = get_date_n_days_ago(1)
        CrashCount.objects.create(version=self.version1, date=yesterday, count=3)

        three_days_ago = get_date_n_days_ago(3)
        CrashCount.objects.create(version=self.version1, date=three_days_ago, count=3)


    def test_get_crash_count_no_param(self):
        res = CrashCount.objects.get_crash_count()
        self.assertEqual(len(res), 2)

    def test_get_crash_count_versions(self):
        res = CrashCount.objects.get_crash_count(versions=[self.version1])
        self.assertEqual(len(res), 2)

        res = CrashCount.objects.get_crash_count(versions=[self.version2])
        self.assertEqual(len(res), 0)

    def test_get_crash_count_time(self):
        res = CrashCount.objects.get_crash_count(time=1)
        self.assertEqual(len(res), 1)

        res = CrashCount.objects.get_crash_count(time=3)
        self.assertEqual(len(res), 2)

    def test_get_crash_count_complete(self):
        res = CrashCount.objects.get_crash_count(time=2, versions=[self.version1])
        self.assertEqual(len(res), 1)

        res = CrashCount.objects.get_crash_count(time=5, versions=[self.version2])
        self.assertEqual(len(res), 0)
