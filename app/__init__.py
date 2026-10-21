#!/usr/bin/python3

from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns

# Application factory: each call builds a Flask app, while imported namespaces
# and the module-level facade remain shared within the Python process.
def create_app():
    app = Flask(__name__)
    # Flask-RESTX manages the HTTP API and its interactive Swagger documentation
    # exposed at /api/v1/.
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')

    # Register the users namespace
    # Namespaces group routes by resource. These prefixes combine with
    # the relative @api.route paths declared in each module.
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path = '/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    return app