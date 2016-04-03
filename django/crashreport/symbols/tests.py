from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User

import os, zipfile

from .models import SymbolsUpload

def get_test_file_path(file_name):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, "testdata/%s" % (file_name))

class TestSimpleSymbolsUpload(TestCase):

    def setUp(self):
        user = User.objects.create_user('test user')
        self.c = Client()
        self.c.force_login(user)

    def test_symbols_upload_valid_zip(self):
        comment = 'Test Comment'
        with open(get_test_file_path("valid.zip")) as f:
            response = self.c.post('/upload/', {'symbols':f, 'comment': comment})
        self.assertEqual(response.status_code, 200)
        uploaded_symbols = SymbolsUpload.objects.all()
        self.assertEqual(len(uploaded_symbols), 1)
        uploaded_symbol = uploaded_symbols[0]
        self.assertEqual(uploaded_symbol.comment, comment)
        self.assertListEqual(uploaded_symbol.files.splitlines(), ['file1', 'file2'])

    def test_sybols_upload_invalid_zip(self):
        with open(get_test_file_path("invalid.zip")) as f:
            with self.assertRaises(zipfile.BadZipfile):
                response = self.c.post('/upload/', {'symbols': f, 'comment': 'Test Comment'})

    def test_missing_comment(self):
        with open(get_test_file_path("valid.zip")) as f:
            response = self.c.post('/upload/', {'symbols':f})
        self.assertEqual(response.status_code, 405)

    def test_missing_file(self):
        response = self.c.post('/upload/', {'comment': 'test comment'})
        self.assertEqual(response.status_code, 405)
