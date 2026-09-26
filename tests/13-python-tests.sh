#!/bin/sh
#
# Python application tests (pytest over tests/test_*.py).
#
# Tier: tool-gated (python3, pytest, and the application dependencies).
#
# The suite needs PyQt6, OpenCV, NumPy, sounddevice, vosk, and piper. Those are
# heavy dependencies, so the test skips cleanly when they are not importable
# instead of failing the repository check suite. Run it in the project
# virtualenv:
#
#     make install && make test-python
#
# A live camera, microphone, and speaker are not required: the tests import the
# modules and exercise their pure logic.
set -eu

DIRECTORY_SCRIPT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPOSITORY_ROOT=$(CDPATH= cd -- "$DIRECTORY_SCRIPT/.." && pwd)

. "$DIRECTORY_SCRIPT/lib/test_helpers.sh"
skip_unless_tool python3

# Prefer the project virtualenv when it exists.
if [ -x "$REPOSITORY_ROOT/.venv/bin/python" ]; then
    PYTHON_BIN="$REPOSITORY_ROOT/.venv/bin/python"
else
    PYTHON_BIN=python3
fi

if ! "$PYTHON_BIN" -c 'import pytest' >/dev/null 2>&1; then
    skip_test "missing dependency: pytest (run make install)"
fi

if ! "$PYTHON_BIN" -c 'import PyQt6, cv2, numpy, sounddevice' >/dev/null 2>&1; then
    skip_test "missing dependency: application runtime (run make install)"
fi

cd "$REPOSITORY_ROOT"
"$PYTHON_BIN" -m pytest -q tests
echo '13-python-tests: ok'
exit 0
