# Agent Entry Point

This file is the entry point for a coding agent working in this repository.
It is orientation only: it points at the authoritative files and defines no
rule of its own. Where this file and an authoritative file differ, the
authoritative file governs (`prompts/01-contract.md` section 2).

## Read First

- `prompts/01-contract.md` — authority, precedence, interaction, output, safety.
- `prompts/02-workflow.md` — the execution sequence; its section 1 lists the
  mandatory baseline, in order, and the task-relevant files to load after it.
- `prompts/03-conventions.md` — formatting, naming, and repository structure.

## Then

- The task: `prompts/how-to-write-tasks.md` defines the format a task must
  have.
- The feature requirements the task references: `prompts/features/`.
- The state: `TODO.md` (status, not authorization) and `PHASES.md`.
- The record forms: `records/README.md`.

## Commands

- `make test` — the repository check suite; it writes a log under `logs/`.
- `make status` — the current phase, the next open TODO item, the last test
  result, and the working-tree state, in one screen.
- `make site`, `make release`, `make install` — see the `Makefile`.

## Tool-Specific Files

- A tool-specific file (`.aider.conf.yml`, `CLAUDE.md`,
  `.github/copilot-instructions.md`, or similar) points here or holds
  mechanical configuration; it must not restate a rule.
- `prompts/` is the only place a rule is defined.

## How this project does it

- Psyche1 is a Python 3.10+ desktop application built with PyQt6, with sources under `sources/`.
- `make install` creates `.venv` and installs `requirements.txt`; `make run` launches the application.
- `make test` runs the shell check suite and, when their dependencies are importable, the Python tests in `tests/test_*.py`; the wrapper is `tests/13-python-tests.sh`.
- The feature index is `prompts/features/00-features.md`.
