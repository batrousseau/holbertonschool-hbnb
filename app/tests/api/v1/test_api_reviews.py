#!/usr/bin/python3
import unittest
import uuid
from app import create_app
from app.services import facade

class TestReviewApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.global_path = "/api/v1/reviews/"
        unique_id = str(uuid.uuid4())
        self.owner = facade.create_user({"first_name": "John", "last_name": "Doe", "email": f"review.{unique_id}@example.com"})
        self.amenity = facade.create_amenity({"name": f"Review Wifi {unique_id}"})
        self.place = facade.create_place({"title": f"Review Place {unique_id}", "description": "Place for reviews", "price": 100.0, "latitude": 44.8, "longitude": -0.5, "owner_id": self.owner.id, "amenities": [self.amenity.id]})

    def test_post_review(self):
        with self.subTest("Correct review"):
            review_data = {"text": "Great place", "rating": 5, "user_id": self.owner.id, "place_id": self.place.id}
            response = self.client.post(self.global_path, json=review_data)
            self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
            data = response.get_json()
            self.assertIn("id", data)
            self.assertEqual(data["rating"], 5)
            self.assertEqual(data["user_id"], self.owner.id)
            self.assertEqual(data["place_id"], self.place.id)

    def test_get_review(self):
        review_data = {"text": "Review for GET", "rating": 4, "user_id": self.owner.id, "place_id": self.place.id}
        response = self.client.post(self.global_path, json=review_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["id"]
        with self.subTest("Existing review"):
            response = self.client.get(f"{self.global_path}{review_id}")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["id"], review_id)
            self.assertEqual(data["text"], "Review for GET")
            self.assertEqual(data["rating"], 4)
            self.assertEqual(data["user_id"], self.owner.id)
            self.assertEqual(data["place_id"], self.place.id)
        with self.subTest("Unknown review"):
            response = self.client.get(f"{self.global_path}{uuid.uuid4()}")
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertEqual(data["error"], "Review not found")

    def test_get_all_reviews(self):
        review_data = {"text": "Review for GET all", "rating": 3, "user_id": self.owner.id, "place_id": self.place.id}
        response = self.client.post(self.global_path, json=review_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["id"]
        response = self.client.get(self.global_path)
        self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
        data = response.get_json()
        self.assertIn(review_id, data)
        returned_review = data[review_id]
        self.assertEqual(returned_review["text"], "Review for GET all")
        self.assertEqual(returned_review["rating"], 3)
        self.assertEqual(returned_review["user_id"], self.owner.id)
        self.assertEqual(returned_review["place_id"], self.place.id)

    def test_put_review(self):
        review_data = {"text": "Review before update", "rating": 2, "user_id": self.owner.id, "place_id": self.place.id}
        response = self.client.post(self.global_path, json=review_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["id"]
        updated_data = {"text": "Review after update", "rating": 5, "user_id": self.owner.id, "place_id": self.place.id}
        with self.subTest("Existing review"):
            response = self.client.put(f"{self.global_path}{review_id}", json=updated_data)
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertEqual(data["id"], review_id)
            self.assertEqual(data["text"], "Review after update")
        with self.subTest("Verify update"):
            response = self.client.get(f"{self.global_path}{review_id}")
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["text"], "Review after update")
            self.assertEqual(data["rating"], 5)
        with self.subTest("Unknown review"):
            response = self.client.put(f"{self.global_path}{uuid.uuid4()}", json=updated_data)
            self.assertEqual(response.status_code, 404, response.get_data(as_text=True))

    def test_delete_review(self):
        review_data = {"text": "Review to delete", "rating": 1, "user_id": self.owner.id, "place_id": self.place.id}
        response = self.client.post(self.global_path, json=review_data)
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        review_id = response.get_json()["id"]
        with self.subTest("Existing review"):
            response = self.client.delete(f"{self.global_path}{review_id}")
            self.assertEqual(response.status_code, 200, response.get_data(as_text=True))
            data = response.get_json()
            self.assertEqual(data["message"], "Successfully deleted review")
        with self.subTest("Verify deletion"):
            response = self.client.get(f"{self.global_path}{review_id}")
            self.assertEqual(response.status_code, 404)
        with self.subTest("Unknown review"):
            response = self.client.delete(f"{self.global_path}{uuid.uuid4()}")
            self.assertEqual(response.status_code, 404, response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()