#!/usr/bin/python3

from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

# The facade coordinates models and repositories on behalf of API routes.
# It does not construct HTTP responses or define JSON contracts.
class HBnBFacade:
    def __init__(self):
        # Separate repositories hold users, places, reviews and amenities.
        # They all use the same in-memory implementation.
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    def create_user(self, user_data):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def create_place(self, place_data):
        place = Place(**place_data)
        self.place_repo.add(place)
        return place

    def create_review(self, review_data):
        # The ** operator expands JSON dictionary keys into constructor arguments.
        # Model validation runs before the new Review is stored.
        review = Review(**review_data)
        self.review_repo.add(review)
        place = self.get_place(review.place_id)
        # A Review pointing to a Place does not automatically update Place.reviews.
        # The facade maintains that reverse relationship explicitly.
        place.add_review(review.id)
        # vars(place) returns the instance __dict__, not an independent copy.
        # The in-memory repository already holds this same Place by reference.
        # This additional update invokes the Place update/validation methods.
        self.place_repo.update(place.id, vars(place))
        return review

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity


    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_place_by_title(self, title):
        return self.place_repo.get_by_attribute('title', title)

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_amenity_by_name(self, name):
        return self.amenity_repo.get_by_attribute('name', name)

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_review_by_place(self, place_id):
        # get_by_attribute() uses next(), so this returns ONE Review or None,
        # even when multiple reviews share the same place_id.
        return self.review_repo.get_by_attribute('place_id', place_id)


    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_all_places(self):
        return self.place_repo.get_all()



    def update_user(self, user_data):
        user_id = user_data['id']
        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    def update_amenity(self, amenity_id, amenity_data):
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.amenity_repo.get(amenity_id)

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)
        return self.place_repo.get(place_id)

    def update_review(self, review_id, review_data):
        # The Review object is updated first. If its place_id changes, this code
        # does not reconcile the old and new Places' reviews lists.
        self.review_repo.update(review_id, review_data)
        review = self.get_review(review_id)
        place = self.get_place(review.place_id)
        self.update_place(place.id, vars(place))
        return self.review_repo.get(review_id)


    def delete_review(self, review_id):
        review = self.get_review(review_id)
        place = self.get_place(review.place_id)
        # Remove the ID from the Place before deleting the Review object.
        # Otherwise the Place GET contract could follow a dangling review ID.
        place.remove_review(review_id)
        self.review_repo.delete(review_id)
