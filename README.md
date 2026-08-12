# Psyche1

Project structure:
* `sources/` -- contains project source code
  * `main.py` -- application entry point
  * `main_window.py` -- main window UI
  * `audio_io.py` -- asynchronous audio capture/playback
  * `video_capture.py` -- background webcam capture
* `prompts/` -- contains project requirements

* `README.md` -- this file

* `prompts/README.md` -- describes structure of requirements
* `prompts/common/conventions.md` -- describes project conventions
* `prompts/common/workflow.md` -- describes project workflow

* `TODO.md` -- contains list of what to do next, updated regularly

## Setup

Dependencies are managed with `pip` and a virtual environment.
To install everything:

    make install

This will create a virtual environment in `.venv/` (if missing) and
install the packages listed in `requirements.txt`.

If you prefer to do it step by step:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

> **Important**: Do not run `pip install requirements.txt` directly.
> Use the `-r` flag (`pip install -r requirements.txt`) or the
> `make install` target.  The command shown above is the simplest way.

## Running

Start the application with:

