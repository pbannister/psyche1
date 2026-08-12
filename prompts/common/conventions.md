# Convention Conventions

This document defines conventions used for the prompt files in the `prompts/` directory.

## Structure

- `prompts/common/` – requirements that apply to the whole project.
- `prompts/features/` – requirements for individual features.

## Prompt format

All prompt files use Markdown.

### Required sections (when applicable)

- **Context**: A short summary of what the prompt relates to.
- **Goal**: The end result that should be achieved.
- **Constraints**: Any hard constraints (platform, libraries, code style).
- **Examples**: Inline examples of expected input/output.

### Style guidelines

- Use active voice and imperative mood.
- Use `backticks` for file names, function names, and paths.
- Use `**bold**` for emphasis of key terms.
- Use numbered lists or bullet lists for sequence or enumeration.

### Versioning

- Changes to a prompt file must be committed with a descriptive message.
- Major changes must be documented in the file’s header.

## Naming conventions

- File name: lowercase, hyphen-separated words.
- Extension: `.md`.

## Example

prompts/features/logger.md
