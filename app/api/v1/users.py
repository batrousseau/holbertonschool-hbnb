#!/usr/bin/python3

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

# Define the user model for input validation and documentation
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered')
    @api.response(401, 'Invalid input data')
    
    def post(self):
        """Register a new user"""
        user_data = api.payload

        # Simulate email uniqueness check (to be replaced by real validation with persistence)
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return {'id': new_user.id, 'first_name': new_user.first_name, 'last_name': new_user.last_name, 'email': new_user.email}, 201

@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email}, 200

    @api.response(200, 'User details updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Bad request: invalid data')
    def put(self, user_id):
        #we store the information from the payload as a dict and then
        #add the user id from the put method
        received_dict = api.payload
        model_dict = {"first_name" : "x", "last_name": "x","email":"x"}
        for key in received_dict.keys():
            if key not in model_dict:
                return {'error' : 'Bad request'}, 400
        received_dict['id'] = user_id
        #we test the existence of the user by comparing the received id
        #to the ones existing in base
        received_user = facade.get_user(received_dict['id'])
        if not received_user:
            return {'error' : 'User not found'}, 404

        updated_user = facade.update_user(received_dict)
        return {'message': 'Successfully Updated', 'id' : updated_user.id, 'first_name': updated_user.first_name, 'last_name' : updated_user.last_name, 'email' : updated_user.email}, 200


