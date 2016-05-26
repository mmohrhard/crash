from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

import os, zipfile, tempfile

from .models import SymbolsUpload

def get_test_file_path(file_name):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, "testdata/%s" % (file_name))

def remove_dir(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

class TestSimpleSymbolsUpload(TestCase):

    def setUp(self):
        user = User.objects.create_user('test user')
        self.c = Client()
        self.c.force_login(user)
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        remove_dir(self.tmp_dir)

    def test_symbols_upload_valid_zip(self):
        version = '1.2.3.4'
        platform = 'linux'
        with self.settings(SYMBOL_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("valid.zip")) as f:
                response = self.c.post('/upload/', {'symbols':f, 'version': version, 'platform':platform})
        self.assertEqual(response.status_code, 200)
        uploaded_symbols = SymbolsUpload.objects.all()
        self.assertEqual(len(uploaded_symbols), 1)
        uploaded_symbol = uploaded_symbols[0]
        self.assertListEqual(uploaded_symbol.files.splitlines(), ['file1', 'file2'])

    def test_sybols_upload_invalid_zip(self):
        with self.settings(SYMBOL_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("invalid.zip")) as f:
                with self.assertRaises(zipfile.BadZipfile):
                    response = self.c.post('/upload/', {'symbols': f, 'version': '1.2.3.4', 'platform': 'linux'})

    def test_missing_comment(self):
        with self.settings(SYMBOL_UPLOAD_DIR=self.tmp_dir):
            with open(get_test_file_path("valid.zip")) as f:
                response = self.c.post('/upload/', {'symbols':f})
        self.assertEqual(response.status_code, 405)

    def test_missing_file(self):
        with self.settings(SYMBOL_UPLOAD_DIR=self.tmp_dir):
            response = self.c.post('/upload/', {'comment': 'test comment'})
        self.assertEqual(response.status_code, 405)
