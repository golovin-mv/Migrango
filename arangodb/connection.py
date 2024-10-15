from __future__ import annotations

import json
import os

from arangodb.arango_client import ArangoClient


class Connection:
    file_name = "_connection.json"
    client = None

    def __init__(
        self,
        name: str,
        url: str,
        database: str,
        username: str | None = None,
        password: str | None = None,
    ):
        self.name = name
        self.url = url
        self.database = database
        self.username = username
        self.password = password

    def save(self) -> Connection:
        """Save the connection."""
        if Connection.exist(self.name):
            raise Exception(f"Connection {self.name} already exists")

        connections = Connection.get_list()
        connections.append(self.__dict__)

        with open(Connection.file_name, "w", encoding="utf-8") as f:
            json.dump(connections, f)

        return self

    def remove(self) -> None:
        """Remove the connection."""
        connections = Connection.get_list()
        connections = [c for c in connections if c["name"] != self.name]

        with open(Connection.file_name, "w", encoding="utf-8") as f:
            json.dump(connections, f)

    @staticmethod
    def get_list() -> dict:
        Connection.__check_file()
        with open(Connection.file_name, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get(name: str) -> Connection:
        """Get the connection by name."""
        connection = None

        for c in Connection.get_list():
            if c["name"] == name:
                connection = c

        if connection is None:
            raise Exception(f"Connection {name} not found")

        return Connection(**connection)

    @staticmethod
    def __check_file() -> None:
        if not os.path.exists(Connection.file_name):
            with open(Connection.file_name, "w", encoding="utf-8") as f:
                json.dump([], f)

    @staticmethod
    def exist(name: str) -> bool:
        for c in Connection.get_list():
            if c["name"] == name:
                return True
        return False

    def test(self) -> None:
        """Test the connection."""
        client = self.get_client()
        client.get_database.version()

    def get_client(self) -> ArangoClient:
        if self.client is None:
            self.client = ArangoClient(
                url=self.url,
                database=self.database,
                username=self.username,
                password=self.password,
                need_auth=self.username is not None and self.password is not None,
            )

        return self.client
