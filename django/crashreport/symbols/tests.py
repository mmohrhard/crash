from django.test import TestCase
from django.test import Client

import os, zipfile

def get_test_file_path(file_name):
    dir = os.path.dirname(__file__)
    return os.path.join(dir, "testdata/%s" % (file_name))

class TestSimpleSymbolsUpload(TestCase):

    def test_symbols_upload_valid_zip(self):
        c = Client()
        with open(get_test_file_path("valid.zip")) as f:
            response = c.post('/upload/', {'symbols':f, 'comment': 'Test Comment'})
        self.assertEqual(response.status_code, 200)

    def test_sybols_upload_invalid_zip(self):
        c = Client()
        with open(get_test_file_path("invalid.zip")) as f:
            with self.assertRaises(zipfile.BadZipfile):
                response = c.post('/upload/', {'symbols': f, 'comment': 'Test Comment'})
