# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.test import TestCase

from .models import Version

class VersionModelTest(TestCase):
    def setUp(self):
        self.version = Version(major_version=1,
                minor_version=2, micro_version=3,
                patch_version=4)

    def test_version_string(self):
        self.assertEqual(str(self.version), "Version: 1.2.3.4")

    def test_version_string_without_product(self):
        self.assertEqual(self.version.str_without_product(), "1.2.3.4")

class VersionManagerTest(TestCase):
    def setUp(self):
        self.version = Version(major_version=1,
                minor_version=2, micro_version=3,
                patch_version=4)
        self.version.save()

    def test_wrong_version_string(self):
        res = Version.objects.get_by_version_string("2.3.4.5")
        self.assertEqual(len(res), 0)

    def test_short_version_string(self):
        res = Version.objects.get_by_version_string("1.2.3")
        self.assertEqual(len(res), 1)

    def test_full_version_string(self):
        res = Version.objects.get_by_version_string("1.2.3.4")
        self.assertEqual(len(res), 1)

    def test_create_from_string(self):
        res = Version.objects.create_from_string("3.4.5.6")
        self.assertIsNotNone(res)
        self.assertEqual(res.major_version, 3)
        self.assertEqual(res.minor_version, 4)
        self.assertEqual(res.micro_version, 5)
        self.assertEqual(res.patch_version, 6)

    def test_create_from_string_featured(self):
        res = Version.objects.create_from_string("4.5.6.7", featured=True)
        self.assertIsNotNone(res)
        self.assertEqual(res.major_version, 4)
        self.assertEqual(res.minor_version, 5)
        self.assertEqual(res.micro_version, 6)
        self.assertEqual(res.patch_version, 7)
        self.assertEqual(res.featured, True)

    def test_create_from_string_short_version(self):
        with self.assertRaises(Exception):
            Version.objects.create_from_string("5.6.7")

class VersionTest(TestCase):

    def test_get_filter_params(self):
        filter_params = Version.get_filter_params('1.2.3', prefix='test_')
        self.assertEqual(filter_params['test_major_version'], 1)
        self.assertEqual(filter_params['test_minor_version'], 2)
        self.assertEqual(filter_params['test_micro_version'], 3)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
