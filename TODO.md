# TODO

## Open Questions

* [ ] should the main window be made more compact, and how much of the audio UI belongs on the video tab?
* [ ] is a CI pipeline worth adding (optional)?
* [ ] which Vosk and Piper models should be the documented defaults?

## Open Work

* [ ] make the main window more compact.
* [ ] run the Python test suite in an environment with the application dependencies installed.
* [ ] register the project pages with the homelab (`pages_source`) and confirm the leak gate passes.

## Recently Completed

* [x] update the repository to the current `00-project-skeleton` framework (2026-09-26; synced to skeleton commit `b32686a`):
    * [x] adopted the contract, workflow, conventions, common, flavor, and `how-to-write-*` prompt corpus.
    * [x] migrated the old `prompts/common/00-project.md`, `conventions.md`, and `workflow.md` into the new structure and removed them.
    * [x] rewrote every feature in the requirement-identifier format and added `03`–`09` for speech, capture, and the window.
    * [x] added `scripts/`, `tests/` (shell suite), `documents/`, `records/`, `tools/`, `site.in/`, `dataflow.*/`, and `logs/`.
    * [x] adapted `make test` to run the shell check suite plus the tool-gated Python tests.
* [x] make main window more compact
* [x] run tests and pass
* [x] add CI pipeline (optional)
* [x] update method names to match conventions
* [x] add requirements for speech-to-text
* [x] implement speech-to-text (local Vosk)
* [x] add requirements for text-to-speech
* [x] implement text-to-speech module (`sources/text_to_speech.py`)
* [x] integrate text-to-speech controls into main window
* [x] add unit tests for text-to-speech
* [x] generate project conventions
* [x] generate project workflow
* [x] define common requirements
* [x] add conventions and workflow for testing
* [x] document setup and run steps in README
* [x] handle missing PortAudio library gracefully (allow runtime to start without audio)
* [x] fix input underflow warnings (ignore benign warnings, set blocksize to 1024)
* [x] verify `make run` starts without underflow warnings
* [x] add unit tests for audio I/O
* [x] add unit tests for video capture
* [x] run `pytest` and make it pass
* [x] define requirements for facial recognition
* [x] implement facial recognition
* [x] define requirements for voice recognition
* [x] implement voice recognition
* [x] replace Gemini API with local Vosk for voice recognition
* [x] auto-download Vosk model on first run
* [x] show voice recognition status in UI
* [x] add voice detection status indicators (no voice / unrecognized / recognized)
* [x] log face/voice recognition start/stop and recognized names
