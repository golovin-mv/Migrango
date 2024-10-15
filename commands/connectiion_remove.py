from rich.console import Console

from arangodb.connection import Connection


class ConnectionRemoveCommand:
    @staticmethod
    def execute(name: str):
        connection = Connection.get(name)
        connection.remove()
        console = Console()
        console.print(f"[red]Connection [bold]{name}[/bold] removed[/red]")
