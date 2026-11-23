import sounddevice as sd


class AudioStream:
    def __init__(self, sample_rate=44100, chunk_size=2048, device=None):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device = device
        self.stream = None

    def start(self):
        """Initializes and starts the audio input stream using sounddevice."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            device=self.device,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size
        )
        self.stream.start()

    def read(self):
        """Reads a PCM audio frame and returns raw bytes for the DSP pipeline."""
        if self.stream:
            data, overflow = self.stream.read(self.chunk_size)
            return data.tobytes()
        return None

    def stop(self):
        """Safely stops and closes the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
