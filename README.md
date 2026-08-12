# Psyche1

Project structure:
* `sources/` -- contains project source code
  * `main.py` -- application entry point
  * `main_window.py` -- main window UI
  * `audio_io.py` -- asynchronous audio capture/playback
  * `video_capture.py` -- background webcam capture
  * `face_recognition.py` -- face detection and recognition
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

> **Important**: Always use a virtual environment when installing Python
> packages in this project. Do not run `pip install -r requirements.txt`
> with your system Python; it is externally managed and will refuse to
> install packages (PEP 668).
>
> If you see an error like `externally-managed-environment`, either run
> `make install` or create and activate a virtual environment as shown above
> before running `pip`.

## Running

Start the application with:

