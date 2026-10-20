#!/usr/bin/python3

from app.models.user import User, BaseModel


class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner_id, amenities=None, reviews=None):
        super().__init__()
        self.validate_places_credentials(title, description, price, latitude, longitude, owner_id)
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.reviews = list(reviews) if reviews is not None else []
        self.amenities = list(amenities) if amenities is not None else []
        self.owner_id = owner_id

    def validate_places_credentials(self, title, description, price, latitude, longitude, owner_id):
        if type(title) is not str:
            raise TypeError("The title of the place must be a string")
        if len(title) > 100:
            raise ValueError("Too long ! Place must be 100 characters max")
        if type(description) is not str:
            raise TypeError("The description of the place must be a string")
        if type(price) is int:
            price = float(price)
        elif type(price) is not float:
            raise TypeError("The price must be a float")
        if price <= 0:
            raise ValueError("The price must be more than zero !")
        if type(latitude) is int:
            latitude = float(latitude)
        elif type(latitude) is not float:
            raise TypeError("Latitude must be a float")
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError("The latitude must be within -90.0 and 90.0 degree")
        if type(longitude) is int:
            longitude = float(longitude)
        elif type(longitude) is not float:
            raise TypeError("Longitude must be a float")
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError("The longitude must be within -180.0 and 180.0 degree")
        if type(owner_id) is not str:
            raise TypeError("The owner id must be a string")
        if '-' not in owner_id:
            raise ValueError("The owner must be an id")

    def update(self, updated_data):
        new_title = updated_data['title']
        new_description = updated_data['description']
        new_price = updated_data['price']
        new_latitude = updated_data['latitude']
        new_longitude = updated_data['longitude']
        new_owner_id = updated_data['owner_id']
        self.validate_places_credentials(new_title, new_description, new_price, new_latitude, new_longitude, new_owner_id)
        if updated_data.get('amenities'):
            for amenity_id in updated_data['amenities']:
                if amenity_id not in self.amenities:
                    self.add_amenity(amenity_id)
        if updated_data.get('reviews'):
            for review_id in updated_data['reviews']:
                if review_id not in self.reviews:
                    self.add_review(review_id)
        cleaned_data: dict = {'title' : new_title, 'description' : new_description, 'price' : new_price, 'latitude' : new_latitude, 'longitude' : new_longitude, 'owner_id' : new_owner_id}
        super().update(cleaned_data)


    def add_review(self, review_id):
        if not '-' in review_id:
            raise ValueError("the review must be a legit Review")
        self.reviews.append(review_id)
        super().save()

    def add_amenity(self, amenity_id):
        if '-' not in amenity_id:
            raise ValueError("this doesn't seem to be a legit amenity")
        self.amenities.append(amenity_id)
        super().save()