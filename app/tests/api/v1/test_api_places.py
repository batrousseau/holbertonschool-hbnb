#!/usr/bin/python3
import unittest
import uuid
from app import create_app
from app.services import facade

class TestPlaceApi(unittest.TestCase):
    # Flask's test client calls routes in-process, without a running server.
    # The facade stays shared, so UUID-based fixtures avoid collisions.
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.global_path = "/api/v1/places/"
        unique_id = str(uuid.uuid4())
        self.owner = facade.create_user({"first_name": "John", "last_name": "Doe", "email": f"john.{unique_id}@example.com"})
        self.amenity = facade.create_amenity({"name": f"Wifi-{unique_id}"})

    def test_post_place(self):
        with self.subTest("Correct place"):
            place_data = {"title": f"Post Place {uuid.uuid4()}", "description": "A nice place to stay", "price": 100.0, "latitude": 44.8378, "longitude": -0.5792, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
            response = self.client.post(self.global_path, json=place_data)
            self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
            data = response.get_json()
            self.assertIn("id", data)
            self.assertEqual(data["title"], place_data["title"])
            self.assertEqual(data["description"], place_data["description"])
            self.assertEqual(data["price"], place_data["price"])
            self.assertEqual(data["latitude"], place_data["latitude"])
            self.assertEqual(data["longitude"], place_data["longitude"])
            self.assertEqual(data["owner_id"], self.owner.id)
        with self.subTest("Place without description"):
            place_data = {"title": f"Post Place Without Description {uuid.uuid4()}", "price": 80.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
            response = self.client.post(self.global_path, json=place_data)
            self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
            self.assertEqual(response.get_json()["description"], "")

    # Build Place and Review through HTTP, then verify that the detail
    # contract expands related IDs into nested owner/amenity/review data.
    def test_get_place(self):
        place_data = {"title": f"Get Place {uuid.uuid4()}", "description": "Place used for GET", "price": 90.0, "latitude": 44.7, "longitude": -0.4, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
        response = self.client.post(self.global_path, json=place_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        place_id = response.get_json()["id"]
        review_data = {"text": "Review for GET place", "rating": 4, "user_id": self.owner.id, "place_id": place_id}
        response = self.client.post("/api/v1/reviews/", json=review_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["id"]
        with self.subTest("Existing place"):
            response = self.client.get(f"{self.global_path}{place_id}")
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertEqual(data["id"], place_id)
            self.assertEqual(data["title"], place_data["title"])
            self.assertEqual(data["description"], place_data["description"])
            self.assertEqual(data["price"], place_data["price"])
            self.assertEqual(data["latitude"], place_data["latitude"])
            self.assertEqual(data["longitude"], place_data["longitude"])
            self.assertEqual(data["owner_id"], self.owner.id)
            self.assertEqual(data["owner"]["id"], self.owner.id)
            self.assertEqual(data["owner"]["first_name"], self.owner.first_name)
            self.assertEqual(data["owner"]["last_name"], self.owner.last_name)
            self.assertEqual(data["owner"]["email"], self.owner.email)
            self.assertIsInstance(data["amenities"], list)
            amenity = next((item for item in data["amenities"] if item["id"] == self.amenity.id), None)
            self.assertIsNotNone(amenity)
            self.assertEqual(amenity["name"], self.amenity.name)
            self.assertIsInstance(data["reviews"], list)
            review = next((item for item in data["reviews"] if item["id"] == review_id), None)
            self.assertIsNotNone(review)
            self.assertEqual(review["text"], review_data["text"])
            self.assertEqual(review["rating"], review_data["rating"])
            self.assertEqual(review["user_id"], self.owner.id)
        with self.subTest("Unknown place"):
            response = self.client.get(f"{self.global_path}{uuid.uuid4()}")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.get_json()["error"], "Place not found")

    # The API must return a list even though repository storage is a dict
    # keyed by UUID. Compare results by ID without depending on ordering.
    def test_get_all_places(self):
        place_data_1 = {"title": f"First Place {uuid.uuid4()}", "description": "First place", "price": 100.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
        place_data_2 = {"title": f"Second Place {uuid.uuid4()}", "description": "Second place", "price": 150.0, "latitude": 45.0, "longitude": -0.6, "owner_id": self.owner.id, "amenities": [self.amenity.id]}

        response_1 = self.client.post(self.global_path, json=place_data_1)
        response_2 = self.client.post(self.global_path, json=place_data_2)
        self.assertEqual(response_1.status_code, 201, response_1.get_data(as_text=True))
        self.assertEqual(response_2.status_code, 201, response_2.get_data(as_text=True))

        place_id_1 = response_1.get_json()["id"]
        place_id_2 = response_2.get_json()["id"]
        self.assertNotEqual(place_id_1, place_id_2)

        response = self.client.get(self.global_path)
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        data = response.get_json()
        self.assertIsInstance(data, list)

        returned_places = {place["id"]: place for place in data}
        self.assertIn(place_id_1, returned_places)
        self.assertIn(place_id_2, returned_places)
        self.assertEqual(returned_places[place_id_1]["title"], place_data_1["title"])
        self.assertEqual(returned_places[place_id_2]["title"], place_data_2["title"])
        self.assertEqual(returned_places[place_id_1]["price"], 100.0)
        self.assertEqual(returned_places[place_id_2]["price"], 150.0)

    # Check the immediate update response AND a later GET.
    # Amenity associations are additive: existing IDs remain after PUT.
    def test_put_place(self):
        place_data = {"title": f"Put Place {uuid.uuid4()}", "description": "Place used for PUT", "price": 120.0, "latitude": 44.5, "longitude": -0.2, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
        response = self.client.post(self.global_path, json=place_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        place_id = response.get_json()["id"]
        new_amenity = facade.create_amenity({"name": f"Parking-{uuid.uuid4()}"})
        updated_data = {"title": "Updated Put Place", "description": "Updated description", "price": 200.0, "latitude": 45.0, "longitude": -0.6, "owner_id": self.owner.id, "amenities": [new_amenity.id]}
        with self.subTest("Existing place"):
            response = self.client.put(f"{self.global_path}{place_id}", json=updated_data)
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertEqual(data["id"], place_id)
            self.assertEqual(data["title"], updated_data["title"])
        with self.subTest("Verify update"):
            response = self.client.get(f"{self.global_path}{place_id}")
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertEqual(data["title"], updated_data["title"])
            self.assertEqual(data["description"], updated_data["description"])
            self.assertEqual(data["price"], updated_data["price"])
            self.assertEqual(data["latitude"], updated_data["latitude"])
            self.assertEqual(data["longitude"], updated_data["longitude"])
            amenity_ids = [amenity["id"] for amenity in data["amenities"]]
            self.assertIn(self.amenity.id, amenity_ids)
            self.assertIn(new_amenity.id, amenity_ids)
        with self.subTest("Unknown place"):
            response = self.client.put(f"{self.global_path}{uuid.uuid4()}", json=updated_data)
            self.assertEqual(response.status_code, 404, response.get_data(as_text=True))

    # Use two Reviews for one Place to detect single-result lookups that
    # would incorrectly discard other matching reviews.
    def test_get_reviews_by_place(self):
        place_data = {"title": f"Place With Reviews {uuid.uuid4()}", "description": "Place used to test reviews", "price": 100.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner.id, "amenities": [self.amenity.id]}
        response = self.client.post(self.global_path, json=place_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        place_id = response.get_json()["id"]
        review_data_1 = {"text": "Excellent séjour", "rating": 5, "user_id": self.owner.id, "place_id": place_id}
        review_data_2 = {"text": "Appartement agréable", "rating": 4, "user_id": self.owner.id, "place_id": place_id}
        response_1 = self.client.post("/api/v1/reviews/", json=review_data_1)
        response_2 = self.client.post("/api/v1/reviews/", json=review_data_2)
        self.assertEqual(response_1.status_code, 201, response_1.get_data(as_text=True))
        self.assertEqual(response_2.status_code, 201, response_2.get_data(as_text=True))
        review_id_1 = response_1.get_json()["id"]
        review_id_2 = response_2.get_json()["id"]
        with self.subTest("Existing place"):
            response = self.client.get(f"{self.global_path}{place_id}/reviews")
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
            reviews = {review["id"]: review for review in data}
            self.assertIn(review_id_1, reviews)
            self.assertIn(review_id_2, reviews)
            self.assertEqual(reviews[review_id_1]["text"], review_data_1["text"])
            self.assertEqual(reviews[review_id_1]["rating"], review_data_1["rating"])
            self.assertEqual(reviews[review_id_2]["text"], review_data_2["text"])
            self.assertEqual(reviews[review_id_2]["rating"], review_data_2["rating"])
        with self.subTest("Unknown place"):
            response = self.client.get(f"{self.global_path}{uuid.uuid4()}/reviews")
            self.assertEqual(response.status_code, 404, response.get_data(as_text=True))
            self.assertEqual(response.get_json()["error"], "Place not found")

    # A missing relationship is represented by an empty JSON list,
    # not None, an empty dictionary or an absent field.
    def test_get_place_without_reviews(self):
        place_data = {"title": f"Place Without Reviews {uuid.uuid4()}", "description": "No reviews yet", "price": 80.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner.id, "amenities": []}
        response = self.client.post(self.global_path, json=place_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        place_id = response.get_json()["id"]
        response = self.client.get(f"{self.global_path}{place_id}")
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        data = response.get_json()
        self.assertEqual(data["reviews"], [])
        self.assertEqual(data["amenities"], [])
        self.assertEqual(data["owner"]["id"], self.owner.id)

if __name__ == "__main__":
    unittest.main()