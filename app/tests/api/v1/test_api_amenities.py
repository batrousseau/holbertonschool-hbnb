#!/usr/bin/python3

import unittest
from app import create_app

class TestAmenityApi(unittest.TestCase):
    # Create an in-process HTTP client for these API-level assertions.
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.global_path = "api/v1/amenities/"

    # Exercise both successful creation and an invalid JSON schema.
    def test_post_amenity(self):
        with self.subTest("Correct Amenity"):
            response = self.client.post(path=self.global_path, json={'name' : 'lounge'})
            assert response.status_code == 201
        with self.subTest("Invalid data"):
            response = self.client.post(path=self.global_path, json={'what': 'dafuck'})
            assert response.status_code == 400

    # Insert multiple items before querying the collection; the current
    # API contract uses an ID-keyed dictionary, not a JSON list.
    def test_get_all_amenities(self):
        amenities = ['pool', 'dishwasher', 'bronze tiger', 'plasma tv']
        for element in amenities:
            self.client.post(path= self.global_path, json={'name' : element})
        response = self.client.get(path=self.global_path)
        assert response.status_code == 200

    def test_get_amenity(self):
        with self.subTest("Correct Amenity"):
            first_post = self.client.post(path=self.global_path, json={'name' : 'wifi'})
            data = first_post.get_json()
            new_adress = self.global_path + data['id']
            response = self.client.get(path= new_adress)
            assert response.status_code == 200
            assert data['name'] in response.text
        with self.subTest("Amenity not found"):
            wrong_id = '1234'
            new_adress = self.global_path + wrong_id
            response = self.client.get(path= new_adress)
            assert response.status_code == 404


    def test_put_amenity(self):
        with self.subTest("Correct User"):
            first_post = self.client.post(path=self.global_path, json={'name' : 'internet'})
            data = first_post.get_json()
            new_adress = self.global_path + data['id']
            response = self.client.put(path=new_adress, json={'name': 'fast internet'})
            assert response.status_code == 200
        with self.subTest("Amenity not found"):
            id = "3456"
            new_adress = self.global_path + id
            response = self.client.put(path=new_adress, json={'name' : 'something idk'})
            assert response.status_code == 404