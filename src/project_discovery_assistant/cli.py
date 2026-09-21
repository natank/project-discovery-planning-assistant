"""Command-line entry point for the Project Discovery and Planning Assistant."""

import typer

app = typer.Typer(
    help="Explore and plan a software project from an initial idea.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run the Project Discovery and Planning Assistant."""


if __name__ == "__main__":
    app()
