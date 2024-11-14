import json
import os
from typing import Callable

from arangodb.arango_client import ArangoClient


class ExportManager:
    def __init__(self, client: ArangoClient, migration_path: str) -> None:
        """
        Initialize the class instance.

        Args:
            client (ArangoClient): The ArangoDB client object.
            migration_path (str): The path to the migrations directory.
        """
        self.client = client
        self.migration_path = migration_path
        self.counter = 1

    def make_migration_files(self, on_collection_exported: Callable[[], None]) -> None:
        """
        Generates migration files for all collections in the client.
        This function iterates over all collections in the client and generates a migration file for each collection.
        The migration file contains the JSON representation of all documents in the collection.
        """

        if not os.path.exists(self.migration_path):
            os.makedirs(self.migration_path)

        for collection in self.client.get_all_collections():
            json_content = json.dumps(self.client.get_all_documents(collection["name"]))
            self.__write_migration_file(self.__generate_file_name(collection["name"]), json_content)
            on_collection_exported()

    def __write_migration_file(self, file_name: str, json_content: str) -> None:
        with open(os.path.join(self.migration_path, file_name), "w") as f:
            f.write(json_content)
            self.counter += 1

    def __generate_file_name(self, collection_name: str) -> str:
        return f"{self.counter:016}_{collection_name}.json"
