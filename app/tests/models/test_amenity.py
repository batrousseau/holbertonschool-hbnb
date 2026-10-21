#!/usr/bin/python3

from datetime import datetime
import unittest

from app.models.user import BaseModel
from app.models.amenity import Amenity


# Model tests are independent of Flask/RESTX request validation.
# Here we test the constructor and its domain-level constraints.
class TestAmenity(unittest.TestCase):

    def setUp(self):
        self.amenity = Amenity(name="Wi-Fi")

    def test_base_model_fields(self):
        self.assertIsInstance(self.amenity, BaseModel)
        self.assertIsNotNone(self.amenity.id)
        self.assertIsInstance(self.amenity.id, str)
        self.assertIsInstance(self.amenity.created_at, datetime)
        self.assertIsInstance(self.amenity.updated_at, datetime)

    def test_name_field(self):
        self.assertIsInstance(self.amenity.name, str)
        self.assertNotEqual(self.amenity.name, "")
        self.assertLessEqual(len(self.amenity.name), 50)

    def test_name_errors(self):
        with self.subTest("Wrong type"):
            with self.assertRaises(TypeError):
                Amenity(42)

        with self.subTest("Empty name"):
            with self.assertRaises(ValueError):
                Amenity("")

        with self.subTest("Name too long"):
            with self.assertRaises(ValueError):
                Amenity("a" * 51)