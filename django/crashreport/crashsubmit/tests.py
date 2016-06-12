from django.test import TestCase
from django.test import Client
from django.db.models import signals

from base.models import Version

from models import UploadedCrash
from signals import process_uploaded_crash

import os
import tempfile
import json

def get_test_file_path(file_name):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, "testdata/%s" % (file_name))

def remove_dir(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

def find_crash_id(response):
    crash_id_split = response.content.split('=')
    return crash_id_split[1]

def find_crash(response):
    id = find_crash_id(response)
    upload_crash = UploadedCrash.objects.get(crash_id=id)
    return upload_crash

class TestCrashUpload(TestCase):

    def setUp(self):
        self.version = Version.objects.create(major_version = 1,
                minor_version = 2, micro_version = 3, patch_version = 4)
        self.tmp_dir = tempfile.mkdtemp()
        signals.post_save.disconnect(process_uploaded_crash, sender=UploadedCrash)

    def tearDown(self):
        remove_dir(self.tmp_dir)

    def test_uploadCorrectCrash(self):
        c = Client()
        with self.settings(TEMP_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("test")) as f:
                response = c.post('/submit/', {'upload_file_minidump':f, 'Version': '1.2.3.4'})
        self.assertEqual(response.status_code, 200)

    def test_uploadInvalidVersion(self):
        c = Client()
        with self.settings(TEMP_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("test")) as f:
                response = c.post('/submit/', {'upload_file_minidump':f, 'Version': '2.3.4.5'})
        self.assertEqual(response.status_code, 500)

    def test_uploadInvalidFile(self):
        c = Client()
        response = c.post('/submit/', {'Version': self.version})
        self.assertEqual(response.status_code, 400)

    def test_uploadMetadata(self):
        c = Client()
        with self.settings(TEMP_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("test")) as f:
                response = c.post('/submit/', {'upload_file_minidump':f, 'Version': '1.2.3.4'})
        self.assertEqual(response.status_code, 200)

    def test_uploadDeprecatedAttribs(self):
        c = Client()
        with self.settings(TEMP_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("test")) as f:
                response = c.post('/submit/', {'upload_file_minidump':f, 'Version': '1.2.3.4', 'AdapterDeviceId': 'Device1', 'AdapterVendorId': 'Vendor1'})
        self.assertEqual(response.status_code, 200)

    def test_uploadJsonAttribs(self):
        c = Client()
        with self.settings(TEMP_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("test")) as f:
                response = c.post('/submit/', {'upload_file_minidump':f, 'Version': '1.2.3.4', 'AdditionalData': '{ "key1" : "val1", "key2" : "val2"}'})
        self.assertEqual(response.status_code, 200)
        upload_crash = find_crash(response)
        self.assertIsNotNone(upload_crash)
        json_data = json.loads(upload_crash.additional_data)
        self.assertDictEqual(json_data, { 'key1': 'val1', 'key2': 'val2'})
