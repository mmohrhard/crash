from django.test import TestCase, Client
from django.contrib.auth.models import User

from django.utils import timezone

from processor.models import Signature, ProcessedCrash

class TestAddBugReport(TestCase):

    def setUp(self):
        user = User.objects.create_user('test user')
        self.c = Client()
        self.c.force_login(user)

    def _create_signature(self, signature):
        self.signature = Signature()
        self.signature.signature = signature
        self.signature.first_observed = timezone.now()
        self.signature.last_observed = timezone.now()
        self.signature.save()

    def test_add_bug(self):
        self._create_signature("my_signature")

        response = self.c.post('/management/add-bug', {'signature': 'my_signature', 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)

    def test_add_bug_multiple_times(self):
        my_signature_str = "my_signature2"
        self._create_signature(my_signature_str)

        response = self.c.post('/management/add-bug', {'signature': my_signature_str, 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)
        response = self.c.post('/management/add-bug', {'signature': my_signature_str, 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)

    def test_add_bug_through_crash_id(self):
        my_signature_str = "my_signature3"
        self._create_signature(my_signature_str)

        crash_id = my_signature_str + "1"
        ProcessedCrash.objects.create(upload_time=timezone.now(),
                signature = self.signature,
                crash_id = crash_id)
        response = self.c.post('/management/add-bug', {'signature': crash_id, 'bug_nr': '1234'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)
