import os

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument("image")
@click.argument("argv", nargs=-1)
def run(
    image: str,
    argv: list
):
    argv = list(argv)

    os.execv(argv[0], argv)


if __name__ == "__main__":
    cli()
