# TODO

## Completed

* [x] generate project conventions
* [x] generate project workflow
* [x] define common requirements
* [x] add conventions and workflow for testing
* [x] document setup and run steps in README
* [x] handle missing PortAudio library gracefully (allow runtime to start without audio)
* [x] fix input underflow warnings (ignore benign warnings, set blocksize to 1024)
* [x] verify `make run` starts without underflow warnings

## Next Up

* [ ] add unit tests for audio I/O
* [ ] add unit tests for video capture
* [ ] run `pytest` and make it pass
* [ ] add CI pipeline (optional)
