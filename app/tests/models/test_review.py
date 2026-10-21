#!/usr/bin/python3

from datetime import datetime
import unittest
import uuid
from app.models.user import User, BaseModel
from app.models.place import Place
from app.models.review import Review


# These tests target the Review model directly rather than Flask.
# ID validation here is about format, not repository existence.
class TestReview(unittest.TestCase):

    def setUp(self):
        self.user = User("John", "Doe", f"john.@example.com")

        self.place = Place(
            "My place",
            "Nice place",
            100,
            45.0,
            2.0,
            self.user.id
        )

        self.review = Review(
            "Very nice place",
            5,
            self.place.id,
            self.user.id
        )

    def test_base_model_fields(self):
        self.assertIsInstance(self.review, BaseModel)
        self.assertIsNotNone(self.review.id)
        self.assertIsInstance(self.review.id, str)
        self.assertIsInstance(self.review.created_at, datetime)
        self.assertIsInstance(self.review.updated_at, datetime)

    def test_text_field(self):
        self.assertIsInstance(self.review.text, str)
        self.assertNotEqual(self.review.text, "")

    def test_rating_field(self):
        self.assertIsInstance(self.review.rating, int)
        self.assertGreaterEqual(self.review.rating, 1)
        self.assertLessEqual(self.review.rating, 5)

    def test_place_field(self):
        self.assertIs(self.review.place_id, self.place.id)

    def test_user_field(self):
        self.assertIs(self.review.user_id, self.user.id)

    def test_text_errors(self):
        with self.subTest("Wrong type"):
            with self.assertRaises(TypeError):
                Review(42, 5, self.place.id, self.user.id)

        with self.subTest("Empty text"):
            with self.assertRaises(ValueError):
                Review("", 5, self.place, self.user.id)

    # Keep type validation separate from checking the valid range 1..5.
    def test_rating_errors(self):
        with self.subTest("Wrong type"):
            with self.assertRaises(TypeError):
                Review("Nice place", "5", self.place, self.user.id)

        with self.subTest("Rating too high"):
            with self.assertRaises(ValueError):
                Review("Nice place", 6, self.place, self.user.id)

        with self.subTest("Rating too low"):
            with self.assertRaises(ValueError):
                Review("Nice place", 0, self.place, self.user.id)

    def test_place_errors(self):
        with self.subTest("Wrong type"):
            with self.assertRaises(ValueError):
                Review("Nice place", 5, "not a place", self.user.id)

    def test_user_errors(self):
        with self.subTest("Wrong type"):
            with self.assertRaises(ValueError):
                Review("Nice place", 5, self.place.id, "not a user")