import os
import re
from rich.progress import Progress

from deepdiff import DeepDiff, Delta
from rich.console import Console

from arangodb.connection import Connection
from migration.php_arango_migration_creator import PhpArangoMigrationCreator


class MakeMigrationsCommand:
    @staticmethod
    def execute(
        output_dir: str, reference_connection_name: str, compared_connection_name: str
    ):
        console = Console()
        with Progress() as progress:
            reference_connection = Connection.get(reference_connection_name)
            compared_connection = Connection.get(compared_connection_name)

            collections_len = len(
                compared_connection.get_client().get_all_collections()
            )

            task = progress.add_task("[green]Comparing...", total=collections_len + 1)
            progress.update(task, advance=1)

            while not progress.finished:
                mismatches = reference_connection.get_client().compare_collections(
                    compared_connection.get_client(), lambda: None
                )

                if len(mismatches) == 0:
                    progress.stop()
                    return console.print("[green]Collections are equal[/green]")

                progress.update(task, advance=collections_len - len(mismatches))

                migration_creator = PhpArangoMigrationCreator()

                for mismatch in mismatches:
                    migration_creator.add_diff(
                        mismatch["name"],
                        Delta(
                            MakeMigrationsCommand.__get_diff(
                                reference_connection,
                                compared_connection,
                                mismatch["name"],
                                console,
                            )
                        ).to_flat_dicts(),
                    )
                    progress.update(task, advance=1)
                progress.stop()

                MakeMigrationsCommand.create_and_write_file(
                    output_dir, migration_creator.create_migration()
                )

    @staticmethod
    def __get_diff(
        reference_connection: Connection,
        compared_connection: Connection,
        collection_name: str,
        console: Console,
    ) -> DeepDiff:
        exclude_rev = re.compile(r"root\[[A-z0-9\/'-\.]+\]\['_rev'\]")
        exclude_key = re.compile(r"root\[[A-z0-9\/']+\-\.]\['_key'\]")

        return DeepDiff(
            {
                item["_id"]: item
                for item in reference_connection.get_client().get_all_documents(
                    collection_name
                )
            },
            {
                item["_id"]: item
                for item in compared_connection.get_client().get_all_documents(
                    collection_name
                )
            },
            exclude_regex_paths=[exclude_rev, exclude_key],
            verbose_level=2,
        )

    @staticmethod
    def create_and_write_file(file_path: str, data: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(data)
