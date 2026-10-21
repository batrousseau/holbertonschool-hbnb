# HBnB — REST API (Holberton School, Part 2)

An educational Airbnb-style backend built with **Python**, **Flask**, and **Flask-RESTX**. It exposes versioned REST endpoints for users, amenities, places, and reviews.

**Project status:** implementation of the business logic and REST API with **in-memory persistence**. This repository does **not** currently use SQLAlchemy or a database. Stored data is lost when the Python process stops.

## Features

- Create, retrieve, and update users and amenities.
- Create, list, retrieve, and update places.
- Create, list, retrieve, update, and delete reviews.
- Associate amenities with places by their IDs.
- Automatically add a newly created review's ID to its place through the facade.
- Return detailed place information with expanded owner, amenities, and reviews.
- Generate interactive API documentation with Flask-RESTX.
- Run unit tests and API tests using Python's `unittest`.

## Architecture

```text
HTTP client
    |
    v
Flask-RESTX API (app/api/v1/)
    |
    v
HBnBFacade (app/services/facade.py)
    |
    +--> Domain models (app/models/)
    |      User, Amenity, Place, Review, BaseModel
    |
    +--> InMemoryRepository (app/persistence/repository.py)
```

The API layer handles HTTP requests and JSON responses. The facade coordinates model operations and repository access. Domain models perform their own field validation. The repository stores Python objects in dictionaries keyed by UUID.

**Relationships:** a `Place` keeps lists of amenity IDs and review IDs; a `Review` also stores `place_id` and `user_id`. On review creation, `HBnBFacade.create_review()` calls `place.add_review(review.id)`. Detailed place responses resolve these IDs into nested JSON objects using `rebuild_contract_from_place()`.

## Project structure

```text
.
├── app/
│   ├── __init__.py                 # Flask app factory, namespaces, API docs
│   ├── api/v1/
│   │   ├── amenities.py
│   │   ├── places.py
│   │   ├── reviews.py
│   │   └── users.py
│   ├── models/
│   │   ├── amenity.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py                 # User and BaseModel
│   ├── persistence/repository.py   # Abstract repository + in-memory implementation
│   ├── services/facade.py
│   └── tests/
│       ├── api/v1/                 # HTTP endpoint tests
│       └── models/                 # Domain model tests
├── config.py
├── requirments.txt                 # Filename as currently committed
├── run.py
└── README.md
```

## Requirements and installation

- Python 3.10+ (the project uses standard Python 3 and was developed with Python 3.10)
- `pip`

From the repository root:

```bash
git clone https://github.com/batrousseau/holbertonschool-hbnb.git
cd holbertonschool-hbnb

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirments.txt
```

On Windows PowerShell, activate the environment using `.venv\Scripts\Activate.ps1`.

**Note:** the dependency file is currently named `requirments.txt` (not `requirements.txt`). It lists `flask` and `flask-restx`.

## Run the API

```bash
python3 run.py
```

The development server normally runs at **http://127.0.0.1:5000**.

- **Swagger / interactive API docs:** http://127.0.0.1:5000/api/v1/
- **API prefix:** `/api/v1`

`run.py` currently starts Flask with `debug=True`; use this only for local development.

## API endpoints

| Resource | Method | Endpoint | Current behavior |
| --- | --- | --- | --- |
| Users | POST | `/api/v1/users/` | Create a user; reject duplicate email |
| Users | GET | `/api/v1/users/<user_id>` | Retrieve one user |
| Users | PUT | `/api/v1/users/<user_id>` | Update a user |
| Amenities | POST | `/api/v1/amenities/` | Create an amenity; reject duplicate name |
| Amenities | GET | `/api/v1/amenities/` | Dictionary keyed by amenity ID |
| Amenities | GET | `/api/v1/amenities/<amenity_id>` | Retrieve one amenity |
| Amenities | PUT | `/api/v1/amenities/<amenity_id>` | Update an amenity |
| Places | POST | `/api/v1/places/` | Create a place; reject duplicate title |
| Places | GET | `/api/v1/places/` | List of place objects (summary fields) |
| Places | GET | `/api/v1/places/<place_id>` | Detailed place, including owner, amenities, reviews |
| Places | PUT | `/api/v1/places/<place_id>` | Update a place |
| Places | GET | `/api/v1/places/<place_id>/reviews` | List of review objects for that place |
| Reviews | POST | `/api/v1/reviews/` | Create a review and associate it with its place |
| Reviews | GET | `/api/v1/reviews/` | Dictionary keyed by review ID |
| Reviews | GET | `/api/v1/reviews/<review_id>` | Retrieve one review |
| Reviews | PUT | `/api/v1/reviews/<review_id>` | Update a review |
| Reviews | DELETE | `/api/v1/reviews/<review_id>` | Delete a review from its repository |

Successful POST requests return **201**, most GET and PUT requests return **200**, and unknown individual resources generally return **404**. Error handling for invalid payloads is not yet uniform.

### JSON contracts

**Create a place:** the `owner_id` and entries in `amenities` are ID strings, not nested objects. `description` defaults to an empty string if omitted.

```json
{
  "title": "Maison Bordeaux",
  "description": "A nice place to stay",
  "price": 120.0,
  "latitude": 44.8378,
  "longitude": -0.5792,
  "owner_id": "<existing-user-uuid>",
  "amenities": ["<existing-amenity-uuid>"]
}
```

**Create a review:**

```json
{
  "text": "Great stay",
  "rating": 5,
  "user_id": "<existing-user-uuid>",
  "place_id": "<existing-place-uuid>"
}
```

**Detailed place GET:** returns an object containing the place's fields, an `owner` object, an `amenities` array of `{id, name}` objects, and a `reviews` array of `{id, text, rating, user_id}` objects. A place without amenities or reviews returns empty arrays.

**Reviews-by-place GET:** `GET /api/v1/places/<place_id>/reviews` returns the **array directly**, not an object keyed by `place_id`.

**PUT payloads:** the current place model's update method expects `title`, `description`, `price`, `latitude`, `longitude`, and `owner_id`. The review update method expects `text`, `rating`, `place_id`, and `user_id`. Partial updates are not consistently supported.

## End-to-end example (curl)

Run the API first, then use these commands in a second terminal. Python is used to extract IDs from the JSON responses, so `jq` is not required.

```bash
BASE="http://127.0.0.1:5000/api/v1"

USER_JSON=$(curl -s -X POST "$BASE/users/" -H "Content-Type: application/json" \
  -d '{"first_name":"Jane","last_name":"Doe","email":"jane.example@example.com"}')
USER_ID=$(printf '%s' "$USER_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

AMENITY_JSON=$(curl -s -X POST "$BASE/amenities/" -H "Content-Type: application/json" \
  -d '{"name":"WiFi Example"}')
AMENITY_ID=$(printf '%s' "$AMENITY_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

PLACE_JSON=$(curl -s -X POST "$BASE/places/" -H "Content-Type: application/json" \
  -d "{\"title\":\"Sample House\",\"description\":\"Test listing\",\"price\":100.0,\"latitude\":44.8,\"longitude\":-0.5,\"owner_id\":\"$USER_ID\",\"amenities\":[\"$AMENITY_ID\"]}")
PLACE_ID=$(printf '%s' "$PLACE_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')

curl -s -X POST "$BASE/reviews/" -H "Content-Type: application/json" \
  -d "{\"text\":\"Great stay\",\"rating\":5,\"user_id\":\"$USER_ID\",\"place_id\":\"$PLACE_ID\"}"

curl -s "$BASE/places/$PLACE_ID" | python3 -m json.tool
curl -s "$BASE/places/$PLACE_ID/reviews" | python3 -m json.tool
```

Each newly created review is linked to its place by the facade; **no extra PUT request to the place is required**. Use unique emails, amenity names, and place titles when repeating this example in the same server process.

## Tests

Run the full `unittest` suite from the repository root:

```bash
python3 -m unittest discover -v app/tests
```

Run only the places API tests:

```bash
python3 -m unittest -v app.tests.api.v1.test_api_places
```

The repository contains both **domain-model tests** (`app/tests/models/`) and **endpoint tests** (`app/tests/api/v1/`). The endpoint tests use Flask's test client; they do not require a separately running web server.

## Current limitations and next steps

This is a learning project, not a production-ready API.

- **No durable storage:** the repositories are in memory; restarting the process loses data.
- **Incomplete relationship checks:** some model checks only verify that an ID resembles a UUID; not every referenced user, place, or amenity is guaranteed to exist.
- **Review deletion consistency:** the DELETE endpoint removes the review from `review_repo` but does not remove its ID from the related place's `reviews` list. Enriched place retrieval may fail on that stale reference.
- **Review reassignment:** changing a review's `place_id` does not currently reconcile the review lists of the old and new places.
- **Single-result attribute lookup:** `InMemoryRepository.get_by_attribute()` uses `next(..., None)` and returns only the first match. The facade's `get_review_by_place()` therefore does **not** retrieve all reviews for a place.
- **Validation and API errors:** some malformed payloads or broken references can still produce unhandled errors; `@api.expect()` is not equivalent to enforced validation on every route.
- **No authentication or authorization:** the API currently exposes operations without login or access controls.

These are documented implementation boundaries rather than features already completed.

## License

No license file is currently included in this repository.
