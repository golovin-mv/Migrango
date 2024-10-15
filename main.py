import logging
from rich.logging import RichHandler

from cli import cli

if __name__ == "__main__":
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(level=logging.INFO)],
    )

    log = logging.getLogger("rich")
    cli()
