import threading

import numpy as np
import sounddevice as sd


class AudioIO:
    """Asynchronous duplex audio I/O using sounddevice.

    Captures microphone input and plays speaker output simultaneously.
    By default it acts as a loopback (mic -> speaker). Provide callbacks
    to process input or generate output.
    """

    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stream = None
        self._lock = threading.Lock()
        self._is_running = False

    def start(self, input_callback=None, output_callback=None):
        """Start the audio stream.

        Args:
            input_callback: callable(indata: np.ndarray) -> np.ndarray
                Receives the microphone chunk as a float32 numpy array
                and returns data to be played to the speaker.
            output_callback: callable(frames: int) -> np.ndarray
                Receives the number of frames and returns a numpy array
                of shape (frames, channels) to be played.
        """
        def callback(indata, outdata, frames, time_info, status):
            if status:
                print(f"Audio status: {status}")

            if input_callback is not None:
                processed = input_callback(indata.copy())
                outdata[:] = processed
            elif output_callback is not None:
                outdata[:] = output_callback(frames)
            else:
                outdata[:] = indata

        with self._lock:
            if self._is_running:
                raise RuntimeError("Audio stream is already running")

            self.stream = sd.Stream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=callback,
                dtype="float32",
            )
            self.stream.start()
            self._is_running = True

    def stop(self):
        """Stop and close the audio stream if it is running."""
        with self._lock:
            if self._is_running:
                self.stream.stop()
                self.stream.close()
                self.stream = None
                self._is_running = False

    def record(self, duration: float) -> np.ndarray:
        """Record audio for a given duration and return it as a float32 array.

        Args:
            duration: seconds to record.

        Returns:
            numpy.ndarray of shape (int(duration * sample_rate), channels)
        """
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
        )
        sd.wait()
        return audio

    def play(self, data: np.ndarray):
        """Play a numpy array of audio data asynchronously.

        Args:
            data: float32 array of shape (frames, channels) or (frames,)
        """
        sd.play(data, samplerate=self.sample_rate, blocking=False)
