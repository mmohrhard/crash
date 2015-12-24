from django.test import TestCase

from .models import Product

class ProductModelTest(TestCase):
    def test_product_string(self):
        product = Product(product_name="TestProduct")
        product_str = str(product)
        self.assertEqual(product_str, "TestProduct")
