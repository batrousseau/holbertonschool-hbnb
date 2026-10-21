#!/usr/bin/python3
from app.services.facade import HBnBFacade

# This module-level facade is shared by API requests and tests.
# Its in-memory repositories retain objects for the life of the process.
facade = HBnBFacade()