# Project Workflow

This document describes the recommended development process for the Psyche1 project.

## Principles

- Make small, incremental changes.
- Prefer test-driven development for core logic.
- Keep `main` stable at all times.
- Update documentation and TODO lists as the project evolves.

## Flow

1. Identify a need or feature.
2. Add a corresponding requirement file under `prompts/features/` if one does not exist yet.
3. Create a feature branch:
   ```bash
   git checkout -b feature/<feature-name>
   ```
4. Implement the code in `sources/`, following the project conventions in `prompts/common/conventions.md`.
5. Write or update unit tests under `tests/`.
6. Run the test suite:
   ```bash
   pytest
   ```
7. If the change affects audio or video I/O, perform a quick manual smoke test.
8. Commit related changes together with a descriptive commit message in imperative mood.
9. Push the branch and open a merge request.
10. After review, merge the branch into `main`.
11. Update `TODO.md` (mark completed tasks) and adjust `README.md` or prompt files if they are affected.

## Additional Notes

- Pull the latest `main` before starting new work.
- Keep each commit focused on a single logical change.
- Set up the environment with:
  ```bash
  pip install -r requirements.txt
  ```
- If you modify dependencies, update `requirements.txt` in the same commit.
- If you change documentation (`prompts/`, `README.md`), consider committing those changes together with the related code.
- Ask for clarification before implementing if a requirement is ambiguous.
