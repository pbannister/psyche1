# Project Conventions

This document defines conventions for the Psyche1 project.

## Purpose

These conventions ensure consistency across the codebase and make it easier for contributors to understand and modify the project.

## Code Style

- Use Python 3.10+ features where appropriate.
- Follow [PEP 8](https://peps.python.org/pep-0008/) for code layout.
- Use type hints for all public functions and methods.
- Prefer explicit imports over wildcard imports.
- Use `snake_case` for functions, variables, and module names.
- Use `CamelCase` for class names.
- Use `UPPER_CASE` for constants.

* Use structured naming, so related item sort together.
    * Do not use single-word names in other than local scope.
    * As a rule - the larger the scope, the longer the name.
    * Parts of name become increasingly specific.
        * Examples: 
            * window_title_get()
            * title_size, title_font

## Project Structure

- `sources/` contains all application source code.
- `prompts/` contains requirement and convention documents.
- `prompts/common/` holds project-wide conventions and workflow.
- `prompts/features/` holds feature-specific requirements.
- Keep modules focused on a single responsibility.

## Dependencies

- Declare all runtime dependencies in `requirements.txt`.
- Use version ranges (e.g., `>=1.0,<2.0`) to allow compatible updates.
- Avoid adding dependencies without a clear need.

## Documentation

- Write docstrings for all public classes and functions.
- Use Google style docstrings (triple-quoted strings with `Args:` and `Returns:`).
- Keep README.md up to date with the project structure and usage.
- Update TODO.md as tasks are completed or added.

## Git Workflow

- Use descriptive commit messages in the imperative mood (e.g., "Add audio capture module").
- Commit related changes together.
- Keep the `main` branch stable; use feature branches for larger changes.

## Testing

- Write unit tests for core logic.
- Place tests in a `tests/` directory at the project root.
- Use `pytest` as the test runner.
- Aim for high coverage of audio and video I/O modules.

## Error Handling

- Raise specific exceptions with informative messages.
- Do not silently swallow exceptions unless there is a clear reason.
- Log errors using the `logging` module when appropriate.

## Concurrency

- Use `threading` for I/O-bound tasks (audio, video).
- Protect shared state with locks.
- Prefer daemon threads for background tasks that should not block shutdown.
- Avoid blocking the main thread with long-running operations.

## Example

