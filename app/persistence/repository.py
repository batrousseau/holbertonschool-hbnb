#!/usr/bin/python3

from abc import ABC, abstractmethod

# The abstract repository defines storage operations without choosing
# an implementation; business rules belong to domain models and the facade.
class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


# Each repository keeps actual Python object references in a dictionary.
# Data is not persisted to disk and disappears when the process stops.
class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        # Store the object under its UUID string; no serialization or copy occurs.
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        # This creates a new list, but its elements still reference the stored objects.
        return list(self._storage.values())

    def update(self, obj_id, data):
        # Delegate updates to the model's update method, which performs validation
        # and eventually assigns values through BaseModel.update.
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        # getattr dynamically reads the named attribute on each object.
        # The generator selects matches; next() returns only the FIRST one.
        # No match produces None, not an empty list.
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)