# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """Creates a product and verifies that the product exists"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Verify the product
        created_product = Product.find(product.id)
        self.assertEqual(created_product.id, product.id)
        self.assertEqual(created_product.name, product.name)
        self.assertEqual(created_product.description, product.description)
        self.assertEqual(created_product.price, product.price)

    def test_update_a_product(self):
        """Creates a product, updates it, and verifies that the information has changed"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # update the product and verify that the description has changed
        product.description = "This has been updated"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "This has been updated")
        # verify that the updated product has only changed the description
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "This has been updated")

    def test_delete_a_product(self):
        """Creates a product, verifies it exists, deletes it, then verifies it no longer exists"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # verifies that there is only one product
        self.assertEqual(len(Product.all()), 1)
        # removes the product
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """Creates multiple products and verifies they all exist"""
        products = Product.all()
        self.assertEqual(len(products), 0)
        # creates 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # verifies that all 5 products exist
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """Creates multiple products and verifies they all exist"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # finds the name of the first product in the list and counts the number of occurences
        name = products[0].name
        name_count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        # verifies that the the name occurs the same number of times between the manual count and found
        self.assertEqual(found.count(), name_count)
        # verifies that the name is correct
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_availabiltiy(self):
        """Creates multiple products and verifies their availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        available_count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), available_count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_category(self):
        """Creates multiple products and verifies their Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        category_count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), category_count)
        for product in found:
            self.assertEqual(product.category, category)
