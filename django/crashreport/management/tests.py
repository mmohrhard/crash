from django.test import TestCase, Client
from django.contrib.auth.models import User

from django.utils import timezone

from processor.models import Signature

class TestAddBugReport(TestCase):

    def _create_signature(self, signature):
        self.signature = Signature()
        self.signature.signature = signature
        self.signature.first_observed = timezone.now()
        self.signature.last_observed = timezone.now()
        self.signature.save()

    def test_add_bug(self):
        self._create_signature("my_signature")

        user = User.objects.create_user('test user')
        c = Client()
        c.force_login(user)

        response = c.post('/management/add-bug', {'signature': 'my_signature', 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)

    def test_add_bug_multiple_times(self):
        self._create_signature("my_signature")

        user = User.objects.create_user('test user')
        c = Client()
        c.force_login(user)

        response = c.post('/management/add-bug', {'signature': 'my_signature', 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)
        response = c.post('/management/add-bug', {'signature': 'my_signature', 'bug_nr': '1234'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.signature.bugs.all().count(), 1)
