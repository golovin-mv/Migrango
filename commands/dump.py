from arangodb.connection import Connection
from export_manager import ExportManager
from rich.progress import Progress


class DumpCommand:
    @staticmethod
    def execute(connection_name: str, output_dir: str):
        connection = Connection.get(connection_name)
        connection.get_client()

        manager = ExportManager(connection.get_client(), output_dir)
        with Progress() as progress:
            task = progress.add_task(
                "[green]Exporting...",
                total=len(connection.get_client().get_all_collections()),
            )
            while not progress.finished:
                manager.make_migration_files(lambda: progress.update(task, advance=1))
