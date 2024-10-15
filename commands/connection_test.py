from rich.console import Console

from arangodb.connection import Connection


class ConnectionTestCommand:
    @staticmethod
    def execute(name: str):
        console = Console()
        try:
            connection = Connection.get(name)
            connection.test()
            console.print(f"[green]Connection [bold]{name}[/bold] passed!")
        except Exception as ex:
            console = Console()
            console.print(f"[red]Connection [bold]{name}[/bold] failed: {ex}")
