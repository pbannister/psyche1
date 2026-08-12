"""
Audio I/O module using sounddevice for capturing microphone input and
playing speaker output asynchronously.
"""

import sounddevice as sd
import numpy as np
from typing import Callable, Optional


class AudioIO:
    """Manages asynchronous microphone capture and speaker playback."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.sample_rate = sample_rate
        self.input_stream: Optional[sd.InputStream] = None
        self.output_stream: Optional[sd.OutputStream] = None

    def start_capture(
        self,
        callback: Callable[[np.ndarray], None],
        device: Optional[int] = None,
    ) -> None:
        """
        Start capturing microphone audio.

        The supplied *callback* receives a new numpy array of audio samples
        each time a buffer is ready.

        :param callback: function to process captured audio blocks
        :param device:   sounddevice device ID (default system default)
        """
        def input_callback(
            indata: np.ndarray,
            frames: int,
            time_info,
            status,
        ) -> None:
            if status:
                print(f"Audio input status: {status}")
            # Copy the data so the callback can keep its own copy
            callback(indata.copy())

        self.input_stream = sd.InputStream(
            samplerate=self.sample_rate,
            device=device,
            channels=1,
            callback=input_callback,
        )
        self.input_stream.start()

    def start_playback(
        self,
        callback: Callable[[int], np.ndarray],
        device: Optional[int] = None,
    ) -> None:
        """
        Start playback to speakers.

        The user-supplied *callback* receives the number of frames required
        and must return a numpy array of shape (frames,) or (frames,1).

        :param callback: function that generates audio to be played
        :param device:   sounddevice device ID (default None)
        """
        def output_callback(
            outdata: np.ndarray,
            frames: int,
            time_info,
            status,
        ) -> None:
            if status:
                print(f"Audio output status: {status}")
            data = callback(frames)
            data = data.flatten()  # ensure 1‑D if needed
            out_len = len(outdata)
            if len(data) < out_len:
                outdata[:len(data)] = data[:]
                outdata[len(data):] = 0.0
            else:
                outdata[:] = data[:out_len]

        self.output_stream = sd.OutputStream(
            samplerate=self.sample_rate,
            device=device,
            channels=1,
            callback=output_callback,
        )
        self.output_stream.start()

    def stop(self) -> None:
        """Stop all streams and release resources."""
        if self.input_stream is not None:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None
        if self.output_stream is not None:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
