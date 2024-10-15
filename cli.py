import click
from rich.prompt import Prompt

from commands.compare import CompareCommand
from commands.connectiion_remove import ConnectionRemoveCommand
from commands.connection_list import ConnectionListCommand
from commands.connection_test import ConnectionTestCommand
from commands.create_connection import CreateConnectionCommand
from commands.dump import DumpCommand
from commands.make_migrations import MakeMigrationsCommand


@click.group()
def cli():
    """Compare ArangoDB collections. Make migration files."""
    pass


@cli.group()
def connection():
    """Manage connections to ArangoDB."""
    pass


@connection.command(name="list")
def connections_list():
    """Show all connections."""
    ConnectionListCommand.execute()


@connection.command(name="remove")
@click.argument("name", required=True)
def remove_connection(name: str):
    """Remove connection."""
    ConnectionRemoveCommand.execute(name)


@connection.command(name="create")
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    show_default=True,
    default=False,
    help="Enable interactive mode.",
)
@click.argument("name", required=False)
@click.argument("url", required=False)
@click.argument("database", required=False)
@click.argument("username", required=False)
@click.argument("password", required=False)
def create_connection(
    interactive: bool, name: str, url: str, database: str, username: str, password: str
):
    """Create connection."""
    if interactive:
        name = Prompt.ask(
            "[magenta]Connection name[/magenta]",
            default="local",
        )
        url = Prompt.ask(
            "[magenta]Database URL[/magenta]", default="http://localhost:8529"
        )
        database = Prompt.ask("[magenta]Database name[/magenta]", default="_system")
        username = Prompt.ask("[magenta]Username name[/magenta]", default=None)
        password = Prompt.ask("[magenta]Password name[/magenta]", default=None)
    CreateConnectionCommand.execute(name, url, database, username, password)


@connection.command(name="test")
@click.argument("name", required=True)
def test_connection(name: str):
    """Test the connection."""
    ConnectionTestCommand.execute(name)


@cli.command()
@click.option(
    "-c",
    "--checksum-only",
    is_flag=True,
    show_default=True,
    default=False,
    help="Only calculate checksum.",
)
@click.option(
    "-d",
    "--details",
    is_flag=True,
    show_default=True,
    default=False,
    help="Show details.",
)
@click.argument("reference_connection", required=True)
@click.argument("compared_connection", required=True)
def compare(
    reference_connection: str,
    compared_connection: str,
    checksum_only: bool,
    details: bool,
):
    """Compare ArangoDB collections. Make migration files."""
    CompareCommand.execute(
        reference_connection, compared_connection, checksum_only, details
    )


@cli.command(help="Dump all collection from the connection.")
@click.option(
    "-o",
    "--output-dir",
    required=True,
    show_default=True,
    default="./dump",
    help="Output directory.",
)
@click.argument("connection", required=True)
def dump(output_dir: str, connection: str):
    """Dump all collection from the connection."""
    DumpCommand.execute(connection, output_dir)


@cli.command(help="Make migrations files for collections defined in the connection.")
@click.option(
    "-o",
    "--output-dir",
    required=True,
    show_default=True,
    default="./dump",
    help="Output directory.",
)
@click.argument("reference_connection", required=True)
@click.argument("compared_connection", required=True)
def make_migrations(
    output_dir: str, reference_connection: str, compared_connection: str
):
    MakeMigrationsCommand.execute(output_dir, reference_connection, compared_connection)
