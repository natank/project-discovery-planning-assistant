# Project Discovery and Planning Assistant

An end-to-end demonstration project for exploring the CrewAI framework.

The assistant will help turn a software idea into a clearer product direction,
requirements, and an actionable delivery plan. Development is documentation-led
and will progress from vision to product requirements, technical design, and
implementation.

## Project documentation

Development documents are maintained in [`_docs/`](./_docs/).

## Development setup

The project uses Python 3.11 or later (below 3.15), [`uv`](https://docs.astral.sh/uv/)
for dependency management, and a `src/` package layout.

```bash
uv sync --dev
cp .env.example .env
```

The `.env` file is optional for the default test suite and must never be
committed. Provider-dependent commands require a real `OPENAI_API_KEY`; use a
non-sensitive fixture idea when running them.

## Development commands

Run the default, provider-free test suite:

```bash
uv run pytest
```

Check formatting, linting, and types:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
```

The CLI entry point is installed as `pdpa` and currently exposes the command
help surface while application workflow commands are delivered in later
milestones:

```bash
uv run pdpa --help
```

## Local runtime files

Project state will be written under `projects/` during later milestones. Local
environment files, project artifacts, virtual environments, caches, and
provider credentials are excluded from version control.
