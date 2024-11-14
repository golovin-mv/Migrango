import os
import re
from rich.progress import Progress

from deepdiff import DeepDiff, Delta
from rich.console import Console

from arangodb.connection import Connection
from migration.arango_migration_creator import MigrationCreator


class MakeMigrationsCommand:
    @staticmethod
    def execute(output_dir: str, reference_connection_name: str, compared_connection_name: str, template: str):
        console = Console()
        with Progress() as progress:
            reference_connection = Connection.get(reference_connection_name)
            compared_connection = Connection.get(compared_connection_name)

            collections_len = len(compared_connection.get_client().get_all_collections())

            task = progress.add_task("[green]Comparing...", total=collections_len + 1)
            progress.update(task, advance=1)

            while not progress.finished:
                [mismatches, create, delete] = reference_connection.get_client().compare_collections(compared_connection.get_client(), lambda: None)

                if len(mismatches) == 0:
                    progress.stop()
                    return console.print("[green]Collections are equal[/green]")

                progress.update(task, advance=collections_len - len(mismatches))

                migration_creator = MigrationCreator(create, delete, template)

                for mismatch in mismatches:
                    migration_creator.add_diff(
                        mismatch["name"],
                        Delta(
                            MakeMigrationsCommand.__get_diff(
                                reference_connection.get_client().get_all_documents(mismatch["name"]),
                                compared_connection.get_client().get_all_documents(mismatch["name"]),
                            )
                        ).to_flat_dicts(),
                    )
                    progress.update(task, advance=1)

                for create_collection in create:
                    migration_creator.add_diff(
                        create_collection["name"],
                        Delta(
                            MakeMigrationsCommand.__get_diff(
                                [],
                                compared_connection.get_client().get_all_documents(create_collection["name"]),
                            )
                        ).to_flat_dicts(),
                    )

                progress.stop()

                MakeMigrationsCommand.create_and_write_file(output_dir, migration_creator.create_migration())

    @staticmethod
    def __get_diff(
        left: list,
        right: list,
    ) -> DeepDiff:
        exclude_rev = re.compile(r"root\[[A-z0-9\/'-\.]+\]\['_rev'\]")
        exclude_key = re.compile(r"root\[[A-z0-9\/']+\-\.]\['_key'\]")

        return DeepDiff(
            {item["_id"]: item for item in left},
            {item["_id"]: item for item in right},
            exclude_regex_paths=[exclude_rev, exclude_key],
            verbose_level=2,
        )

    @staticmethod
    def create_and_write_file(file_path: str, data: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(data)
