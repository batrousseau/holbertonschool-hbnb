#!/usr/bin/python3

import unittest
from app import create_app



class TestUserApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.global_path = "/api/v1/users/"

    def test_post_user(self):
        with self.subTest("Correct user"):
            response = self.client.post(path=self.global_path, json={"first_name" : "John", "last_name": "Doe", "email": "johndoe@hotmail.com"})
            assert response.status_code == 201
        with self.subTest("Already exist"):
            response = self.client.post(path=self.global_path, json={"first_name" : "John", "last_name": "Doe", "email": "johndoe@hotmail.com"})
            assert response.status_code == 400
        with self.subTest("Invalid data"):
            response = self.client.post(path=self.global_path, json={"fistname" : "j", "last": "40", "email": "bit"})

            assert response.status_code == 400

    def test_get_user(self):
        with self.subTest("Correct user"):
            first_post = self.client.post(path=self.global_path, json={"first_name" : "John", "last_name": "Doe", "email": "johndoe2@hotmail.com"})
            data = first_post.get_json()
            new_adress:str = self.global_path + data["id"]
            response = self.client.get(path=new_adress)
            assert response.status_code == 200
            assert data['id'] in response.text
        with self.subTest("User not found"):
            id = "1234"
            new_adress:str = self.global_path + id
            response = self.client.get(path=new_adress)
            assert response.status_code == 404

    def test_put_user(self):
        with self.subTest("Correct user"):
            first_post = self.client.post(path=self.global_path, json={"first_name" : "Jane", "last_name": "Doe", "email": "janedoe2@hotmail.com"})
            data = first_post.get_json()
            new_adress: str = self.global_path + data['id']
            response = self.client.put(path=new_adress, json= {"first_name" : "Jane-Annie", "last_name": "Doe", "email": "janedoe2@hotmail.com"})
            assert response.status_code == 200
            assert data['id'] in response.text
        with self.subTest("User not found"):
            id = "1234"
            new_adress: str = self.global_path + id
            response = self.client.get(path=new_adress, json = {})
            assert response.status_code == 404
        with self.subTest("Invalid data"):
            first_post = self.client.post(path=self.global_path, json={"first_name" : "Bad", "last_name": "Data", "email": "janedoe2@yahoo.fr"})
            data = first_post.get_json()
            new_adress: str = self.global_path + data['id']
            response = self.client.put(path=new_adress, json= {"This is bad data" : "see", "This is bad data" : "see"})
            assert response.status_code == 400