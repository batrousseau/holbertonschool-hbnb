#!/usr/bin/python3

from app.models.user import User, BaseModel
from app.models.place import Place


class Review(BaseModel):
    def __init__(self,text, rating, place_id, user_id):
        super().__init__()
        self.validate_review_credential(text, rating, place_id, user_id)
        self.text = text
        self.rating = rating
        self.place_id = place_id
        self.user_id = user_id

    def validate_review_credential(self, text, rating, place_id, user_id):
        if type(text) is not str:
            raise TypeError("The text must be a string")
        if text == "":
            raise ValueError("The text must be completed")
        if type(rating) is not int:
            raise TypeError("The rating must be an int")
        if rating < 1 or rating > 5:
            raise ValueError("The rating must be from 1 min to 5 max")
        if not '-' in place_id:
            raise ValueError("The place must be a valid Place")
        if not '-' in user_id:
            raise ValueError("This doesn't seem to be a valid user id")

    def update(self, updated_data):
        new_text = updated_data['text']
        new_rating = updated_data['rating']
        new_place_id = updated_data['place_id']
        new_user_id= updated_data['user_id']
        self.validate_review_credential(new_text, new_rating, new_place_id, new_user_id)
        cleaned_data: dict = {'text' : new_text, 'rating' : new_rating, 'place_id' : new_place_id, 'user_id' : new_user_id}
        super().update(cleaned_data)