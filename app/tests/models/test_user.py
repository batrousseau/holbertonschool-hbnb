#!/usr/bin/python3

from datetime import datetime
import unittest
from app.models.user import User, BaseModel


# Exercise BaseModel/User behavior without an API or persistence layer.
class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(first_name="John", last_name="Doe", email="johndoe@hotmail.com")
    
    def test_validate_base_model_id(self):
        self.assertIsInstance(self.user, BaseModel)
        self.assertTrue(self.user.id is not None)
        self.assertTrue(type(self.user.id) is str)

    def test_base_model_fields(self):
        self.assertTrue(type(self.user.created_at) is datetime)
        self.assertTrue(type(self.user.updated_at) is datetime)

    def test_first_name_field(self):
        self.assertTrue(type(self.user.first_name) is str)
        self.assertTrue(len(self.user.first_name) <= 50)
        self.assertFalse(self.user.first_name == "")

    def test_last_name_field(self):
        self.assertTrue(type(self.user.last_name) is str)
        self.assertTrue(len(self.user.last_name) <= 50)
        self.assertFalse(self.user.last_name == "")

    def test_email_field(self):
        self.assertTrue(type(self.user.email) is str)
        self.assertIn("@", self.user.email)

    def test_is_admin_type(self):
        self.assertIsInstance(self.user.is_admin, bool)

    def test_raise_first_name_error(self):
        with self.subTest("wrong type"):
            with self.assertRaises(TypeError):
                User(35, "doe", "35doe@hotmail.com")
        with self.subTest("empty first name"):
            with self.assertRaises(ValueError):
                User("", "Doe", "35doe@hotmail.com")
        with self.subTest("First name too long"):
            with self.assertRaises(ValueError):
                User("incrediblylongfirstnamelikeohmygodthatissolongicantbeliveit", "Doe", "35doe@hotmail.com")


    def test_raise_last_name_error(self):
        with self.subTest("wrong type"):
            with self.assertRaises(TypeError):
                User("John", 35, "John35@gmail.com")
        with self.subTest("empty last name"):
            with self.assertRaises(ValueError):
                User("John", "", "john@gmail.com")
        with self.subTest("Last name too long"):
            with self.assertRaises(ValueError):
                User("John", "incrediblylongnamelikeohmygodethisissolongicantbelieveit", "x@gmail.com")

    # Check wrong type, empty string and missing '@' as separate cases.
    def test_raise_email_error(self):
        with self.subTest("wrong type"):
            with self.assertRaises(TypeError):
                User("John", "Doe", 35)
        with self.subTest("empty email"):
            with self.assertRaises(ValueError):
                User("John", "Doe", "")
        with self.subTest("missing @"):
            with self.assertRaises(ValueError):
                User("John", "Doe", "wrongemail")

