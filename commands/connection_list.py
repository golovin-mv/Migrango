from rich.console import Console

from arangodb.connection import Connection


class ConnectionListCommand:
    @staticmethod
    def execute():
        console = Console()
        connections = Connection.get_list()

        for connection in connections:
            console.print(
                f'[bold green]{connection["name"]}[/bold green] ([gray]{connection["url"]}[/gray])'
            )
