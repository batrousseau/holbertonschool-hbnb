# AirBnB Clone Project

This project is an AirBnB clone built with Python and Flask. It provides a RESTful API for managing amenities, places, reviews, and users. The application follows a layered architecture to separate concerns between API endpoints, business logic, data models, and persistence mechanisms.

## Directory Structure

```
├── README.md
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── amenities.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       └── users.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── amenity.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   └── repository.py
│   └── services/
│       ├── __init__.py
│       └── facade.py
├── config.py
├── requirements.txt
└── run.py
```

## Roles of Main Folders

- **`app/`**: Contains the main application package.
- **`app/api/`**: Defines API endpoints organized by version (`v1`). Each file (e.g., `amenities.py`, `places.py`) handles specific resources.
- **`app/models/`**: Defines data models for entities like amenities, places, reviews, and users.
- **`app/persistence/`**: Handles data storage and retrieval logic via the repository pattern.
- **`app/services/`**: Contains business logic, including a facade for coordinating operations across layers.
- **`config.py`**: Stores configuration settings (e.g., database URL, API keys).
- **`run.py`**: Entry point to launch the Flask application.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Installation Steps

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Flask application with the following command:
```bash
python run.py
```

The API will be accessible at `http://localhost:5000` (or the port specified in `config.py`).

## Architecture Overview

- **API Layer (`app/api/`)**: Exposes REST endpoints for CRUD operations on amenities, places, reviews, and users.
- **Models Layer (`app/models/`)**: Defines data structures using SQLAlchemy or similar ORM tools.
- **Services Layer (`app/services/`)**: Implements business logic, with a facade to simplify interactions between layers.
- **Persistence Layer (`app/persistence/`)**: Manages database connections and queries via a repository pattern.

This separation ensures modularity, testability, and maintainability of the codebase.