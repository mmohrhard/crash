from django.test import TestCase

from .models import Product, Version

class ProductModelTest(TestCase):
    def test_product_string(self):
        product = Product(product_name="TestProduct")
        product_str = str(product)
        self.assertEqual(product_str, "TestProduct")

class VersionModeltest(TestCase):
    def setUp(self):
        self.product = Product(product_name="TestProduct")
        self.product.save()

    def test_version_string(self):
        version = Version(product=self.product, major_version=1,
                minor_version=2, micro_version=3,
                patch_version=4)
        self.assertEqual(str(version), "TestProduct Version: 1.2.3.4")
