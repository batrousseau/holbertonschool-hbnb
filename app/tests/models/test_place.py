
#!/usr/bin/python3
import unittest
import uuid
from app.models.place import Place


class TestPlace(unittest.TestCase):
    def setUp(self):
        self.owner_id = str(uuid.uuid4())
        self.amenity_id = str(uuid.uuid4())
        self.review_id = str(uuid.uuid4())
        self.valid_data = {"title": "Test Place", "description": "A nice place", "price": 100.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner_id}

    # Merge valid fixture fields with individual overrides so each test
    # can isolate the specific model behavior under examination.
    def create_place(self, **overrides):
        return Place(**{**self.valid_data, **overrides})

    def test_base_model_fields(self):
        place = self.create_place()
        self.assertIsNotNone(place.id)
        self.assertIsInstance(place.id, str)
        self.assertEqual(str(uuid.UUID(place.id)), place.id)
        self.assertIsNotNone(place.created_at)
        self.assertIsNotNone(place.updated_at)

    def test_place_creation(self):
        place = self.create_place()
        self.assertEqual(place.title, "Test Place")
        self.assertEqual(place.description, "A nice place")
        self.assertEqual(place.price, 100.0)
        self.assertEqual(place.latitude, 44.8)
        self.assertEqual(place.longitude, -0.5)
        self.assertEqual(place.owner_id, self.owner_id)
        self.assertEqual(place.amenities, [])
        self.assertEqual(place.reviews, [])

    def test_place_creation_with_relations(self):
        place = self.create_place(amenities=[self.amenity_id], reviews=[self.review_id])
        self.assertEqual(place.amenities, [self.amenity_id])
        self.assertEqual(place.reviews, [self.review_id])

    def test_description_field(self):
        with self.subTest("Empty description"):
            place = self.create_place(description="")
            self.assertEqual(place.description, "")
        with self.subTest("Invalid description"):
            with self.assertRaises(TypeError):
                self.create_place(description=None)

    def test_title_validation(self):
        with self.subTest("Maximum valid length"):
            place = self.create_place(title="A" * 100)
            self.assertEqual(len(place.title), 100)
        with self.subTest("Title too long"):
            with self.assertRaises(ValueError):
                self.create_place(title="A" * 101)
        with self.subTest("Invalid title type"):
            with self.assertRaises(TypeError):
                self.create_place(title=123)

    def test_price_validation(self):
        with self.subTest("Valid float"):
            place = self.create_place(price=50.5)
            self.assertEqual(place.price, 50.5)
        with self.subTest("Valid integer"):
            place = self.create_place(price=50)
            self.assertEqual(place.price, 50)
        with self.subTest("Zero price"):
            with self.assertRaises(ValueError):
                self.create_place(price=0.0)
        with self.subTest("Negative price"):
            with self.assertRaises(ValueError):
                self.create_place(price=-10.0)
        with self.subTest("Invalid price type"):
            with self.assertRaises(TypeError):
                self.create_place(price="100")
        with self.subTest("Boolean price"):
            with self.assertRaises(TypeError):
                self.create_place(price=True)

    def test_latitude_validation(self):
        for latitude in [-90.0, 0.0, 90.0, 45]:
            with self.subTest(latitude=latitude):
                place = self.create_place(latitude=latitude)
                self.assertEqual(place.latitude, latitude)
        for latitude in [-90.1, 90.1]:
            with self.subTest(invalid_latitude=latitude):
                with self.assertRaises(ValueError):
                    self.create_place(latitude=latitude)
        with self.subTest("Invalid latitude type"):
            with self.assertRaises(TypeError):
                self.create_place(latitude="44.8")

    def test_longitude_validation(self):
        for longitude in [-180.0, 0.0, 180.0, -1]:
            with self.subTest(longitude=longitude):
                place = self.create_place(longitude=longitude)
                self.assertEqual(place.longitude, longitude)
        for longitude in [-180.1, 180.1]:
            with self.subTest(invalid_longitude=longitude):
                with self.assertRaises(ValueError):
                    self.create_place(longitude=longitude)
        with self.subTest("Invalid longitude type"):
            with self.assertRaises(TypeError):
                self.create_place(longitude="-0.5")

    def test_owner_id_validation(self):
        with self.subTest("Valid owner ID"):
            place = self.create_place()
            self.assertEqual(place.owner_id, self.owner_id)
        with self.subTest("Invalid owner ID format"):
            with self.assertRaises(ValueError):
                self.create_place(owner_id="invalidid")
        with self.subTest("Invalid owner ID type"):
            with self.assertRaises(TypeError):
                self.create_place(owner_id=123)

    def test_add_amenity(self):
        place = self.create_place()
        amenity_id_2 = str(uuid.uuid4())
        place.add_amenity(self.amenity_id)
        place.add_amenity(amenity_id_2)
        self.assertEqual(len(place.amenities), 2)
        self.assertIn(self.amenity_id, place.amenities)
        self.assertIn(amenity_id_2, place.amenities)

    def test_add_amenity_invalid_id(self):
        place = self.create_place()
        with self.subTest("Invalid ID format"):
            with self.assertRaises(ValueError):
                place.add_amenity("invalidid")
        with self.subTest("Invalid ID type"):
            with self.assertRaises(TypeError):
                place.add_amenity(123)
        self.assertEqual(place.amenities, [])

    def test_add_review(self):
        place = self.create_place()
        review_id_2 = str(uuid.uuid4())
        place.add_review(self.review_id)
        place.add_review(review_id_2)
        self.assertEqual(len(place.reviews), 2)
        self.assertIn(self.review_id, place.reviews)
        self.assertIn(review_id_2, place.reviews)

    def test_add_review_invalid_id(self):
        place = self.create_place()
        with self.subTest("Invalid ID format"):
            with self.assertRaises(ValueError):
                place.add_review("invalidid")
        with self.subTest("Invalid ID type"):
            with self.assertRaises(TypeError):
                place.add_review(123)
        self.assertEqual(place.reviews, [])

    def test_update_place(self):
        place = self.create_place()
        original_id = place.id
        updated_data = {"title": "Updated Place", "description": "New description", "price": 200.0, "latitude": 45.0, "longitude": -0.6, "owner_id": self.owner_id}
        place.update(updated_data)
        self.assertEqual(place.id, original_id)
        self.assertEqual(place.title, "Updated Place")
        self.assertEqual(place.description, "New description")
        self.assertEqual(place.price, 200.0)
        self.assertEqual(place.latitude, 45.0)
        self.assertEqual(place.longitude, -0.6)
        self.assertEqual(place.owner_id, self.owner_id)

    # Place.update adds new relationship IDs without replacing those
    # that were already present.
    def test_update_place_relations(self):
        amenity_id_2 = str(uuid.uuid4())
        review_id_2 = str(uuid.uuid4())
        place = self.create_place(amenities=[self.amenity_id], reviews=[self.review_id])
        updated_data = {**self.valid_data, "amenities": [self.amenity_id, amenity_id_2], "reviews": [self.review_id, review_id_2]}
        place.update(updated_data)
        self.assertEqual(len(place.amenities), 2)
        self.assertEqual(len(place.reviews), 2)
        self.assertIn(self.amenity_id, place.amenities)
        self.assertIn(amenity_id_2, place.amenities)
        self.assertIn(self.review_id, place.reviews)
        self.assertIn(review_id_2, place.reviews)

    def test_update_place_without_relations(self):
        place = self.create_place(amenities=[self.amenity_id], reviews=[self.review_id])
        place.update({**self.valid_data, "title": "New Title"})
        self.assertEqual(place.title, "New Title")
        self.assertEqual(place.amenities, [self.amenity_id])
        self.assertEqual(place.reviews, [self.review_id])

    def test_update_place_invalid_data(self):
        invalid_cases = [
            ("title", 123, TypeError),
            ("description", None, TypeError),
            ("price", -10.0, ValueError),
            ("price", "invalid", TypeError),
            ("latitude", 100.0, ValueError),
            ("longitude", -200.0, ValueError),
            ("owner_id", "invalidid", ValueError)
        ]
        for field, value, exception in invalid_cases:
            with self.subTest(field=field, value=value):
                place = self.create_place()
                invalid_data = {**self.valid_data, field: value}
                with self.assertRaises(exception):
                    place.update(invalid_data)
                self.assertEqual(place.title, self.valid_data["title"])
                self.assertEqual(place.price, self.valid_data["price"])
                self.assertEqual(place.latitude, self.valid_data["latitude"])
                self.assertEqual(place.longitude, self.valid_data["longitude"])

    # Ensure different Place objects never share mutable relationship lists.
    def test_independent_relation_lists(self):
        place_1 = self.create_place(title="Place One")
        place_2 = self.create_place(title="Place Two")
        place_1.add_amenity(self.amenity_id)
        place_1.add_review(self.review_id)
        self.assertNotEqual(place_1.id, place_2.id)
        self.assertEqual(place_1.amenities, [self.amenity_id])
        self.assertEqual(place_1.reviews, [self.review_id])
        self.assertEqual(place_2.amenities, [])
        self.assertEqual(place_2.reviews, [])

    # The constructor copies input lists; later edits to caller-owned lists
    # must not unexpectedly change the Place instance.
    def test_relation_lists_are_copied(self):
        amenities = [self.amenity_id]
        reviews = [self.review_id]
        place = self.create_place(amenities=amenities, reviews=reviews)
        amenities.append(str(uuid.uuid4()))
        reviews.append(str(uuid.uuid4()))
        self.assertEqual(place.amenities, [self.amenity_id])
        self.assertEqual(place.reviews, [self.review_id])


if __name__ == "__main__":
    unittest.main()
