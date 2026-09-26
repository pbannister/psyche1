# Psyche1

Psyche1 is a Linux desktop application for multimodal capture and presentation.
It combines audio I/O, webcam video, face detection and recognition, voice
recognition, speech to text, and text to speech in one PyQt6 window.
Everything runs locally: no audio, video, or text leaves the machine after the
optional one-time model downloads.

This repository is structured for collaborative development with a Large
Language Model (LLM).

A coding agent begins at `AGENTS.md`, the tool-neutral entry point. The full
mandatory load order is in `prompts/02-workflow.md` section 1:

- `prompts/01-contract.md` defines the interaction, authority, and safety rules.
- `prompts/02-workflow.md` defines the execution sequence for every task.
- `prompts/03-conventions.md` defines formatting and repository conventions.

- The LLM must follow the workflow defined in `prompts/02-workflow.md` for every task.

Human contributors should begin by reading:

- `prompts/README.md`
- `documents/README.md`

Note there are rules meant only to constrain Aider behavior:

- `tools/aider-rules.md` (Aider users only)

All project features are defined in `prompts/features/` and implemented in `sources/`.

## Features

- Audio I/O and microphone-to-speaker loopback (`prompts/features/07-audio-io.md`)
- Webcam video capture (`prompts/features/08-video-capture.md`)
- Face detection and recognition with OpenCV (`prompts/features/05-facial-recognition.md`)
- Local voice recognition with Vosk (`prompts/features/06-voice-recognition.md`)
- Offline speech to text (`prompts/features/03-speech-to-text.md`)
- Local neural text to speech with Piper (`prompts/features/04-text-to-speech.md`)
- A tabbed PyQt6 main window (`prompts/features/09-main-window.md`)
- The publishing toolchain worked example (`prompts/features/01-site-build.md` and `prompts/features/02-project-pages.md`)

The full feature index is `prompts/features/00-features.md`.

## Top-Level Map

- `README.md` is the project overview.
- `AGENTS.md` is the coding-agent entry point; it points at `prompts/` and defines no rule.
- `TODO.md` tracks pending and completed project tasks.
- `PHASES.md` names the project's phases and the current phase (see `documents/06-project-pages.md`).
- `prompts/` contains LLM interaction rules, common requirements, feature requirements, task definitions, and episode work orders.
- `documents/` contains human-consumption documents: the interaction pattern, worked examples, and tool notes.
- `records/` contains version-controlled outcome, incident, and handoff records.
- `tools/` contains tool-specific rules.
- `tools/aider-rules.md` is used only with Aider.
- `sources/` contains the PyQt6 application modules and the entry point.
- `scripts/` contains project scripts.
- `tests/` contains the shell checks, the shared helpers, and the Python application tests.
- `dataflow.in/` contains input data.
- `dataflow.out/` contains generated data output (not version-controlled).
- `logs/` contains generated logs (not version-controlled).
- `site.in/` contains static-site input.
- `site.out/` contains generated static-site output (not version-controlled).
- `requirements.txt` is the Python dependency manifest.
- `Makefile` drives the build (`make build`), the tests (`make test`), and cleanup (`make clean`).

## Project Settings

- Automatic task commits: disabled (the human owns commits; see `prompts/02-workflow.md` §7.1). Changes are left in the working tree.
- Runtime: Python 3.10 or later.
- Dependencies: `requirements.txt`, installed into `.venv` by `make install`.
- Entry point: `python -m sources.main`, run by `make run`.

## Runtime Requirements

- A Linux desktop session with a webcam and an audio device.
- PortAudio (`libportaudio2`) for `sounddevice`. The application still starts when it is missing, and reports the missing library when audio is used.
- Optional Vosk and Piper model files download on first use into `~/.cache/psyche1/`.

## Worked Example

The repository keeps the skeleton's worked publishing example that exercises the
whole workflow:

- Feature: `prompts/features/01-site-build.md`
- Task: `prompts/tasks/01-site-build-implement.md`
- Script: `scripts/site-build.sh` generates `site.out/` from `site.in/`.
- Tests: `tests/00-skeleton.sh` and `tests/01-site-build.sh`
- Input: `site.in/index.txt` (status page) and `site.in/dashboard.txt`
- Template: `site.in/template.html` provides the HTML page structure.

- Run `make build` to generate the site and `make test` to run the tests.
- The bundled feature is a worked example, not a requirement; it is kept because Psyche1 publishes project pages.

## Project Pages (publishing conventions)

- Psyche1 publishes the standard page set (status, dashboard, condensed
  todo/prompts/documents/records) per `prompts/features/02-project-pages.md` and
  `documents/06-project-pages.md`.
- `make site` builds the full set (`scripts/site-build.sh` +
  `scripts/site-condense.sh`).
- `make check` runs the publish sanitization gate (`scripts/leak-gate.sh`) over
  `site.out/`.
- Publishing goes through the homelab project (homelab-publish): the project
  registers once via `pages_source` and does not push to the web server itself —
  `make deploy` is retired.

## Keeping Current with this Skeleton

- This project keeps its own copy of the shared rule files (`prompts/`, the
  directory READMEs, the reference scripts, and the template); those copies
  drift as the skeleton evolves.
- From the skeleton, `sh scripts/skeleton-diff.sh <project-dir>` reports how a
  project's shared files differ. Rule-file drift is a failure; drift in the
  reference scripts and template is expected when a project adapts them.
- Customize a shared rule document by appending a project section (for example
  `## How this project does it`) and leaving the shared text intact. Do not fork
  it, so the next re-sync stays a small diff.
- Psyche1 was last synced to skeleton commit `b32686a` (2026-09-26).

## Canonical Files

The following filenames are canonical and must not be renamed or duplicated without an explicit task:

- `README.md`
- `AGENTS.md`
- `TODO.md`
- `PHASES.md`
- `Makefile`
- `package.json`
- `.gitignore`
- `requirements.txt` — a project-declared root file: the Python dependency manifest (see `prompts/01-contract.md` section 7).

Tool-specific root files (for example `.aider.conf.yml`, `.aiderignore`) are permitted when a file under `tools/` declares them; see `prompts/01-contract.md` section 7.
