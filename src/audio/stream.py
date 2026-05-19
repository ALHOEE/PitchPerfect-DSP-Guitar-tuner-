import sounddevice as sd
import numpy as np

class AudioStream:
    def __init__(self, sample_rate=44100, chunk_size=4096):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream = None

    def start(self):
        """Initializes and starts the audio input stream using the sounddevice library."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size
        )
        self.stream.start()

    def read(self):
        """Reads a chunk of audio data and converts it to raw bytes for DSP pipeline compatibility."""
        if self.stream:
            # Read audio samples as a numeric array
            data, overflow = self.stream.read(self.chunk_size)
            # Convert to raw bytes to maintain compatibility with the existing DSP logic
            return data.tobytes()
        return None

    def stop(self):
        """Safely stops and closes the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
