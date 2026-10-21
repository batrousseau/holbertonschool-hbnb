#!/usr/bin/python3
from app import create_app

# Create the Flask application before starting the local development server.
app = create_app()

if __name__ == '__main__':
    # Debug mode enables interactive development diagnostics;
    # never expose this setting on a production server.
    app.run(debug=True)