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
                mismatches = reference_connection.get_client().compare_collections(
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
                checksum_only,
                console,
            )

    @staticmethod
    def __print_dif(
        reference_connection: Connection,
        compared_connection: Connection,
        details: bool,
        mismatches: list,
        checksum_only: bool,
        console: Console,
    ):
        mismatches_names = reduce(lambda x, y: x + "\n" + y["name"], mismatches, "")

        if checksum_only:
            return console.print(
                f"[magenta]Collections are not equal:[/magenta] [red]{mismatches_names}[/red]"
            )

        for mismatch in mismatches:
            console.print(f'[red]Collection [bold]{mismatch["name"]}[/bold]: [/red]')
            exclude_rev = re.compile(r"root\[[A-z0-9\/'-\.]+\]\['_rev'\]")
            exclude_key = re.compile(r"root\[[A-z0-9\/']+\-\.]\['_key'\]")
            dif = DeepDiff(
                reference_connection.get_client().get_all_documents(mismatch["name"]),
                compared_connection.get_client().get_all_documents(mismatch["name"]),
                exclude_regex_paths=[exclude_rev, exclude_key],
                verbose_level=2 if details else 1,
                group_by="_id",
            )
            if dif:
                console.print(dif.pretty()) if not details else console.print(dif)
            else:
                console.print("[green]Collections are equal[/green]")
