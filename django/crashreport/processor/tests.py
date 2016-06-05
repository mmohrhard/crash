from django.test import TestCase

from .models import CrashCount, ProcessedCrash
from .processor import MinidumpProcessor

from base.models import Version
from crashsubmit.models import UploadedCrash

import datetime
import os
import tempfile

from django.utils import timezone

def get_date_n_days_ago(num_days):
    return datetime.date.fromordinal(datetime.date.today().toordinal() - num_days)

def get_test_file_path(file_name):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, file_name)

def remove_dir(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

class CrashCountManagerTest(TestCase):

    def setUp(self):
        self.version1 = Version.objects.create(
                major_version=1, minor_version=2, micro_version=3, patch_version=4)
        self.version2 = Version.objects.create(
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

class ProcessCrashTest(TestCase):

    def setUp(self):
        self.version1 = Version.objects.create(
                major_version=1, minor_version=2, micro_version=3, patch_version=4)

        self.submitted_crash = UploadedCrash.objects.create(
                crash_id = 'some id', version = self.version1,
                crash_path = get_test_file_path("testdata/test.dmp"),
                additional_data = '{ "key1": "value1" }')

        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        remove_dir(self.tmp_dir)

    def test_process_crash(self):
        processor = MinidumpProcessor()

        processor.process('some id')

        processed_crash = ProcessedCrash.objects.get(crash_id = 'some id')
        self.assertIsNotNone(processed_crash)

    def test_manager_get_crashes_to_process(self):
        unprocessed_crash = UploadedCrash.objects.create(
                crash_id='some other id', version = self.version1,
                crash_path=get_test_file_path("testdata/test.dmp"),
                additional_data='{ "key1": "value1" }')
        crashes = ProcessedCrash.objects.get_crashed_to_process()
        crashes_ids = list(crashes.values_list('crash_id'))
        self.assertIn('some other id', crashes_ids)
