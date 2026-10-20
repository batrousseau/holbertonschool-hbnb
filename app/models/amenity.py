#!/usr/bin/python3

from app.models.place import Place
from app.models.user import BaseModel, User


class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        self.validate_amenity_credentials(name)
        self.name = name

    def update(self, updated_data):
        new_name = updated_data['name']
        self.validate_amenity_credentials(new_name)
        cleaned_data: dict = {'name' : new_name}
        super().update(cleaned_data)

    def validate_amenity_credentials(self, name):
        if type(name) is not str:
            raise TypeError("The name of the amenity must be a string")
        if len(name) > 50:
            raise ValueError("The name of the amenity must be 50 characters maximum")
        if name == "":
            raise ValueError("The name of the amenity must not be empty")