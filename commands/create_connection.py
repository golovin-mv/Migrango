from rich.console import Console

from arangodb.connection import Connection


class CreateConnectionCommand:
    @staticmethod
    def execute(
        name: str,
        url: str,
        database: str,
        username: str | None = None,
        password: str | None = None,
    ):
        connection = Connection(name=name, url=url, database=database, username=username, password=password)
        connection.save()
        console = Console()
        console.print(f"[green]Connection [bold]{name}[/bold] created[/green]")
