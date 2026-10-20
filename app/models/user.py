#!/usr/bin/python3

import uuid
from datetime import datetime


class BaseModel:
    def __init__(self):
        id_value = str(uuid.uuid4())
        if type(id_value) is not str:
            raise TypeError("id must be a string")
        if id_value is None:
            raise ValueError("id must be attributed")
        self.id = id_value

        created_at = datetime.now()
        if type(created_at) is not datetime:
            raise TypeError("Wrong created_at format")
        self.created_at = created_at

        updated_at = datetime.now()
        if type(updated_at) is not datetime:
            raise TypeError("Wrong updated_at format")
        self.updated_at = updated_at

    def save(self):
        """Update the updated_at timestamp whenever the object is modified."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update the attributes of the object based on the provided dictionary."""
        for key, value in data.items():
            if key == "id" or key == "created_at":
                raise PermissionError("id or creation date can't be modified")
            if hasattr(self, key):
                setattr(self, key, value)

        self.save()


class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False):
        # Collect id, created_at and updated_at from the parent class
        super().__init__()
        self.validate_user_credential(first_name, last_name, email)
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin

    def validate_user_credential(self, first_name, last_name, email):
        if type(first_name) is not str:
            raise TypeError("First name must be a string")
        if first_name == "":
            raise ValueError("First name must be completed")
        if len(first_name) > 50:
            raise ValueError("First name must be 50 characters maximum")
        if type(last_name) is not str:
            raise TypeError("Last name must be a string")
        if last_name == "":
            raise ValueError("Last name must be completed")
        if len(last_name) > 50:
            raise ValueError("Last name must be 50 characters maximum")
        if type(email) is not str:
            raise TypeError("Email must be a string")
        if email == "":
            raise ValueError("Email must be completed")
        if "@" not in email:
            raise ValueError("Email seems to be invalid")

    def update(self, updated_data):
        new_first = updated_data["first_name"]
        new_last = updated_data["last_name"]
        new_mail = updated_data["email"]
        self.validate_user_credential(new_first, new_last, new_mail)
        cleaned_data: dict = {"first_name" : new_first, "last_name": new_last,"email" :new_mail}
        super().update(cleaned_data)

