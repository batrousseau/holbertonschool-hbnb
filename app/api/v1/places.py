from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Adding the review model
review_model = api.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner of the place'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place"""
        place_data = api.payload
        if 'description' not in place_data :
            place_data['description'] = ""
        existing_place = facade.get_place_by_title(place_data['title'])
        if existing_place:
            return {'error' : 'place already created'}, 400
        new_place = facade.create_place(place_data)
        return {'id' : new_place.id,'title' : new_place.title, 'description' : new_place.description, 'price' : new_place.price, 'latitude' : new_place.latitude, 'longitude' : new_place.longitude, 'owner_id' : new_place.owner_id}, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        all_places = facade.get_all_places()
        cleaned_places: list = []
        for places in all_places:
            cleaned_places.append({'id' : places.id, 'title' : places.title, 'description' : places.description, 'price' : places.price, 'latitude' : places.latitude, 'longitude' : places.longitude, 'owner_id' : places.owner_id})
        return cleaned_places, 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        print("GET PLACE - IDs des reviews :", place.reviews)

        contract = rebuild_contract_from_place(place)
        print("GET PLACE - Reviews dans le contrat :", contract["reviews"])

        return contract, 200

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        received_dict = api.payload
        if 'description' not in received_dict:
            received_dict['description'] = ""
        received_place = facade.get_place(place_id)
        if not received_place:
            return {'error' : 'Place not found'}, 404
        updated_place = facade.update_place(place_id, received_dict)
        return {'message' : 'Successfully Updated', 'id' : updated_place.id, 'title' : updated_place.title}, 200

@api.route('/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        existing_place = facade.get_place(place_id)
        if not existing_place:
            return {'error' : 'Place not found'}, 404
        cleaned_reviews: list = []
        for reviews in existing_place.reviews:
            current_reviews = facade.get_review(reviews)
            current_dict = {'id' : current_reviews.id, 'text' : current_reviews.text, 'rating' : current_reviews.rating, 'user_id' : current_reviews.user_id}
            cleaned_reviews.append(current_dict)
        return (cleaned_reviews)

def rebuild_contract_from_place(place):
    amenities_id = place.amenities
    amenities_contract: dict = {'amenities' : []}

    for id in amenities_id:
        current_amenity_object = facade.get_amenity(id)
        rebuild_amenity: dict = {'id' : current_amenity_object.id, 'name' : current_amenity_object.name}
        amenities_contract['amenities'].append(rebuild_amenity)

    reviews_objects = facade.get_reviews_by_place(place.id)
    print(f"A ce stade j'ai bien un objet qui contient toutes les reviews : {reviews_objects}")
    if reviews_objects == None:
        reviews_contract: dict = {'reviews' : []}
    else:
        reviews_id: list = []
        for objects in reviews_objects:
            reviews_id.append(objects.id)
            print(f"J'ajoute la review avec l'id {objects.id} . La liste d'id de reviews vaut maintenant {reviews_id}")
        reviews_contract: dict = {'reviews' : reviews_id}
        print(f"J'ai un dictionnaire review contact constitué comme suit : {reviews_contract}")
        for id in reviews_id:
            current_review_object = facade.get_review(id)
            rebuild_review: dict = {'id' : current_review_object.id, 'text' : current_review_object.text, 'rating' : current_review_object.rating, 'user_id' : current_review_object.user_id}
            reviews_contract['reviews'].append(rebuild_review)

    owner_object = facade.get_user(place.owner_id)
    rebuild_owner = {'id': owner_object.id, 'first_name' : owner_object.first_name, 'last_name' : owner_object.last_name, 'email' : owner_object.email}

    rebuild_contract: dict = {'id' : place.id,  'title' : place.title, 'description': place.description, 'price' : place.price,
                              'latitude' : place.latitude, 'longitude' : place.longitude, 'owner_id' : place.owner_id, 
                              'owner' : rebuild_owner, **amenities_contract, **reviews_contract}

    return rebuild_contract




if __name__ == "__main__":
    user_1 = facade.create_user({"first_name": "John", "last_name": "Doe", "email": "john.doe@test.com"})
    user_2 = facade.create_user({"first_name": "Jane", "last_name": "Smith", "email": "jane.smith@test.com"})
    amenity_1 = facade.create_amenity({"name": "Wifi"})
    amenity_2 = facade.create_amenity({"name": "Parking"})

    place_data = {"title": "Maison Test", "description": "Maison utilisée pour tester le contrat API", "price": 120.0, "latitude": 44.8378, "longitude": -0.5792, "owner_id": user_1.id, "amenities": [amenity_1.id, amenity_2.id]}
    place = facade.create_place(place_data)

    review_1 = facade.create_review({"text": "Très bon séjour", "rating": 5, "user_id": user_2.id, "place_id": place.id})
    review_2 = facade.create_review({"text": "Maison agréable", "rating": 4, "user_id": user_1.id, "place_id": place.id})

    place = facade.get_place(place.id)
    contract = rebuild_contract_from_place(place)

    print("PLACE — IDs des reviews :", place.reviews)
    print("REVIEWS ATTENDUES :", [review_1.id, review_2.id])
    print("CONTRAT RECONSTRUIT :")
    print(contract)

    assert review_1.id in place.reviews
    assert review_2.id in place.reviews
    assert {review["id"] for review in contract["reviews"]} == {review_1.id, review_2.id}
    assert {amenity["id"] for amenity in contract["amenities"]} == {amenity_1.id, amenity_2.id}
    assert contract["owner"]["id"] == user_1.id

    print("CONTRAT VALIDÉ")


