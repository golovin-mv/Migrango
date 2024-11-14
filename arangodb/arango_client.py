from __future__ import annotations

import json
import logging
from typing import Callable

import requests
from arango import ArangoClient as ArangoDbClient
from arango.database import StandardDatabase


class ArangoClient:
    """
    Initializes a new instance of the ArangoApi class.

    Args:
        url (str): The URL of the database.
        database (str): The name of the database.
        username (str, optional): The username for authentication.
        password (str, optional): The password for authentication.
        need_auth (bool, optional): Whether authentication
                                    is required. Defaults to True.
    """

    def __init__(
        self,
        url: str,
        database: str,
        username: str | None = None,
        password: str | None = None,
        need_auth: bool = True,
    ):
        self.__url = url
        self.__database = database
        self.__username = username
        self.__password = password
        self.__need_auth = need_auth
        self.__token = None
        self.__db = ArangoDbClient(self.__url).db(self.__database, username=self.__username, password=self.__password)
        self.logger = logging.getLogger("rich")

    @property
    def get_database(self):
        return self.__db

    def compare_collections(self, other: ArangoClient, on_collection_compared: Callable[[], None]) -> list:
        """
        Compare the collections of this object with the collections of another object.
        Args:
            other (ArangoClient): Another object to compare collections with.
            on_collection_compared (Callable): A callback function to be called for each collection compared.
        Returns:
            booL: True if the collections are equal, False otherwise.
        """
        self_collections = self.get_all_collections()
        other_collections = other.get_all_collections()

        mismatches = []
        if len(self_collections) != len(other_collections):
            self.logger.info(f"Collection count mismatch. {len(self_collections)} != {len(other_collections)}")

        for collection in self_collections:
            if collection["name"] == "migrations":
                continue

            self_checksum = self.__db.collection(collection["name"]).checksum(
                with_rev=False,
                with_data=True,
            )

            other_checksum = other.__db.collection(collection["name"]).checksum(with_rev=False, with_data=True)

            if self_checksum != other_checksum:
                self.logger.debug(f'Collection {collection["name"]} checksum mismatch. {self_checksum} != {other_checksum}')
                mismatches.append(collection)

            on_collection_compared()

        collection_for_create_or_delete = self.__get_collections_for_remove_and_for_crete(other_collections, self_collections)

        return [mismatches, collection_for_create_or_delete["create"], collection_for_create_or_delete["delete"]]

    def get_all_collections(self, sort_by_id: bool = True) -> list:
        """
        Returns a list of all collections in the database.
        Not system collections.

        Raise:
            Exception: If the request fails.
        """
        collections = self.__db.collections()

        if sort_by_id:
            collections.sort(key=lambda x: int(x.get("id", 0)))

        return list(filter(lambda x: "_" not in x.get("name", False), collections))

    def get_all_documents(self, collection_name: str) -> list:
        documents = []
        cursor = self.__db.collection(collection_name).all()

        while not cursor.empty():
            documents.append(cursor.pop())
        cursor.close()
        documents.sort(key=lambda x: str(x.get("_id", 0)))
        return documents

    def __get_headers(self) -> dict:
        """
        Return a dictionary of headers for the request.

        Returns:
            dict: A dictionary containing the headers for the request.
            The keys are the header names and the values are the header values.

        Example:
            >>> __get_headers()
            {'accept': 'application/json', 'authorization': 'some_authorization_token'}
        """
        headers = {
            "accept": "application/json",
        }

        if not self.__need_auth:
            return headers

        headers["authorization"] = self.__authorise()
        return headers

    def __authorise(self) -> str:
        """
        Authorizes the user.

        Returns:
            str: The authorization token.
        """
        if self.__token is None:
            result = requests.post(
                f"{self.__url}/_open/auth/",
                headers={"accept": "application/json"},
                json={"username": self.__username, "password": self.__password},
            )

        self.__token = json.loads(result.text)["jwt"]
        return f"bearer {self.__token}"

    def get_db(self) -> StandardDatabase:
        return self.__db

    def __get_collections_for_remove_and_for_crete(
        self, left_collections: list[dict[str, str]], right_collections: list[dict[str, str]]
    ) -> dict[str, list[dict[str, str]]]:
        return {
            "create": [x for x in left_collections if not any(i["name"] == x["name"] and i["type"] == x["type"] for i in right_collections)],
            "delete": [x for x in right_collections if not any(i["name"] == x["name"] and i["type"] == x["type"] for i in left_collections)],
        }

    def __str__(self):
        return f"{self.__url}/{self.__database}"
