#!/usr/bin/python3

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')

# Define the review model for input validation and documentation
review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        review_data = api.payload
        new_review = facade.create_review(review_data)
        return {'id' : new_review.id, 'rating' : new_review.rating, 'user_id' : new_review.user_id, 'place_id' : new_review.place_id}, 201

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        all_reviews = facade.get_all_reviews()
        cleaned_reviews: dict = {}
        for reviews in all_reviews:
            cleaned_reviews[reviews.id] = {'text' : reviews.text, 'rating' : reviews.rating, 'user_id' : reviews.user_id, 'place_id' : reviews.place_id}
        return cleaned_reviews, 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error' : 'Review not found'}, 404

        return {'id' : review.id, 'text' : review.text, 'rating' : review.rating, 'user_id' : review.user_id, 'place_id' : review.place_id }, 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        received_dict = api.payload
        received_review = facade.get_review(review_id)
        if not received_review:
            return {'error' : 'Review not found'}, 404
        updated_review = facade.update_review(review_id, received_dict)
        return {'message' : 'Successfully Updated', 'id' : updated_review.id, 'text' : updated_review.text}, 200

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        review_to_delete = facade.get_review(review_id)
        if not review_to_delete:
            return {'error' : 'Cannot delete a non existing review'}, 404
        facade.review_repo.delete(review_id)
        return {'message' : 'Successfully deleted review'}, 200