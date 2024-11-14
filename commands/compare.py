import re
from functools import reduce
from rich.progress import Progress

from deepdiff import DeepDiff
from rich.console import Console

from arangodb.connection import Connection


class CompareCommand:
    @staticmethod
    def execute(
        reference_connection_name: str,
        compared_connection_name: str,
        checksum_only: bool,
        details: bool,
    ):
        console = Console()
        with Progress() as progress:
            reference_connection = Connection.get(reference_connection_name)
            compared_connection = Connection.get(compared_connection_name)

            task = progress.add_task(
                "[green]Comparing...",
                total=len(compared_connection.get_client().get_all_collections()),
            )

            while not progress.finished:
                [mismatches, create, delete] = reference_connection.get_client().compare_collections(
                    compared_connection.get_client(),
                    lambda: progress.update(task, advance=1),
                )

            progress.stop()

            if len(mismatches) == 0:
                return console.print("[green]Collections are equal[/green]")

            CompareCommand.__print_dif(
                reference_connection,
                compared_connection,
                details,
                mismatches,
                create,
                delete,
                checksum_only,
                console,
            )

    @staticmethod
    def __print_dif(
        reference_connection: Connection,
        compared_connection: Connection,
        details: bool,
        mismatches: list,
        create: list,
        delete: list,
        checksum_only: bool,
        console: Console,
    ):
        mismatches_names = reduce(lambda x, y: x + "\n" + y["name"], mismatches, "")

        CompareCommand.__print_collections_info(create, delete, console)

        if checksum_only:
            return console.print(f"[magenta]Collections are not equal:[/magenta] [red]{mismatches_names}[/red]")

        for mismatch in mismatches:
            CompareCommand.__print_mismatches(
                mismatch["name"],
                reference_connection.get_client().get_all_documents(mismatch["name"]),
                compared_connection.get_client().get_all_documents(mismatch["name"]),
                details,
                console,
                "_id",
            )

        for c in create:
            CompareCommand.__print_mismatches(
                c["name"],
                [],
                compared_connection.get_client().get_all_documents(c["name"]),
                details,
                console,
            )

        for c in delete:
            CompareCommand.__print_mismatches(
                c["name"],
                reference_connection.get_client().get_all_documents(c["name"]),
                [],
                details,
                console,
            )

    @staticmethod
    def __print_collections_info(create: list, delete: list, console: Console):
        if len(create) > 0:
            console.print(f"[green]Collections to create({len(create)}):[/green]")
            for c in create:
                console.print(f'[green]{c["name"]} - {c['type']}[/green]')
        if len(delete) > 0:
            console.print(f"[red]Collections to delete({len(delete)}):[/red]")
            for c in delete:
                console.print(f'[red]{c["name"]} - {c['type']}[/red]')

    @staticmethod
    def __print_mismatches(collection_name: str, left: list, right: list, details: bool, console: Console, group_by: str | None = None):
        console.print(f"[red]Collection [bold]{collection_name}[/bold]: [/red]")

        exclude_rev = re.compile(r"root\[[A-z0-9\/'-\.]+\]\['_rev'\]")
        exclude_key = re.compile(r"root\[[A-z0-9\/']+\-\.]\['_key'\]")

        dif = DeepDiff(
            left,
            right,
            exclude_regex_paths=[exclude_rev, exclude_key],
            verbose_level=2 if details else 1,
            group_by=group_by,
        )
        if dif:
            console.print(dif.pretty()) if not details else console.print(dif)
        else:
            console.print("[green]Collections are equal[/green]")
