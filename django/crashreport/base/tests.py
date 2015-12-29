# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.test import TestCase

from .models import Product, Version

class ProductModelTest(TestCase):
    def test_product_string(self):
        product = Product(product_name="TestProduct")
        product_str = str(product)
        self.assertEqual(product_str, "TestProduct")

class VersionModelTest(TestCase):
    def setUp(self):
        self.product = Product(product_name="TestProduct")
        self.product.save()
        self.version = Version(product=self.product, major_version=1,
                minor_version=2, micro_version=3,
                patch_version=4)

    def test_version_string(self):
        self.assertEqual(str(self.version), "TestProduct Version: 1.2.3.4")

    def test_version_string_without_product(self):
        self.assertEqual(self.version.str_without_product(), "1.2.3.4")

class VersionManagerTest(TestCase):
    def setUp(self):
        self.product = Product(product_name="TestProduct")
        self.product.save()
        self.version = Version(product=self.product, major_version=1,
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

class VersionTest(TestCase):

    def test_get_filter_params(self):
        filter_params = Version.get_filter_params('1.2.3', prefix='test_')
        self.assertEqual(filter_params['test_major_version'], '1')
        self.assertEqual(filter_params['test_minor_version'], '2')
        self.assertEqual(filter_params['test_micro_version'], '3')

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
