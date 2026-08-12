# TODO

* [ ] add CI pipeline (optional)


## Completed

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
