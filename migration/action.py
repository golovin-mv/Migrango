from enum import Enum


class ActionType(Enum):
    COLLECTION_CREATE = "create_collection"
    DELETE_COLLECTION = "delete_collection"
    DOCUMENT_CREATE = "create_document"
    DOCUMENT_DELETE = "delete_document"
    DOCUMENT_UPDATE = "update_document"


class Action:
    def __init__(self, action_type: ActionType, data: dict, collection_name: str):
        self.type = action_type
        self.data = data
        self.collection_name = collection_name

    def __dict__(self):
        return {"data": self.data, "collection_name": self.collection_name}

    def __repr__(self):
        return f"{self.type} - {self.data}"

    def __str__(self):
        return f"{self.type} - {self.data}"
