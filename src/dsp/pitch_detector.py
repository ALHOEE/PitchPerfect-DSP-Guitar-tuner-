import numpy as np
from dsp.pitch_quantizer import GuitarStringQuantizer


class PitchDetector:
    """
    Real-time fundamental frequency (f0) detector using:
    - RMS Noise Gate (S0: IDLE)
    - Hann Window + Zero-Padded FFT + HPS (S1: PROCESSING)
    - Parabolic Interpolation & LUT Classification (S2: PITCH CLASSIFICATION)
    - 3-Frame Stability Timer / Hysteresis Lock (S3: LOCKED)
    """

    def __init__(self, sample_rate=44100, chunk_size=2048, rms_threshold=15.0):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.fft_size = 16384  # Zero-padding for finer frequency grid
        self.rms_threshold = rms_threshold

        # FSM state tracking (~140ms lock = 3 consecutive 46.4ms frames)
        self.state = "IDLE"
        self.required_matches = 3
        self.consecutive_matches = 0
        self.last_string = None

    def find_pitch(self, audio_data):
        # Convert PCM int16 bytes to float64 and remove DC offset
        signal = np.frombuffer(audio_data, dtype=np.int16).astype(np.float64)
        signal -= np.mean(signal)

        # --- S0: IDLE (RMS Noise Gate) ---
        rms = np.sqrt(np.mean(signal ** 2))
        if rms < self.rms_threshold:
            self._reset_fsm()
            return None, 0.0

        # --- S1: PROCESSING (Hann Window + FFT + HPS) ---
        self.state = "PROCESSING"
        window = np.hanning(len(signal))
        windowed_signal = signal * window

        spectrum = np.fft.rfft(windowed_signal, n=self.fft_size)
        magnitude = np.abs(spectrum)

        # Harmonic Product Spectrum (suppresses harmonic ghosting)
        hps_order = 3
        hps_mag = magnitude.copy()
        for ratio in range(2, hps_order + 1):
            downsampled = magnitude[::ratio]
            hps_mag[:len(downsampled)] *= downsampled

        # Digital Band-Pass mask for guitar fundamentals (60Hz - 420Hz)
        freq_resolution = self.sample_rate / self.fft_size
        min_bin = int(60.0 / freq_resolution)
        max_bin = int(420.0 / freq_resolution)
        hps_mag[:min_bin] = 0
        hps_mag[max_bin:] = 0

        peak_bin = int(np.argmax(hps_mag))
        if peak_bin <= min_bin or peak_bin >= len(magnitude) - 1 or hps_mag[peak_bin] == 0:
            self._reset_fsm()
            return None, 0.0

        # Parabolic interpolation around peak bin for fine frequency estimation
        alpha = magnitude[peak_bin - 1]
        beta = magnitude[peak_bin]
        gamma = magnitude[peak_bin + 1]
        denom = alpha - 2.0 * beta + gamma
        p = 0.5 * (alpha - gamma) / denom if denom != 0 else 0.0
        p = float(np.clip(p, -0.5, 0.5))

        f0 = (peak_bin + p) * freq_resolution

        # --- S2: PITCH CLASSIFICATION (LUT Mapping) ---
        self.state = "PITCH_CLASSIFICATION"
        tuning_result = GuitarStringQuantizer.match_guitar_string(f0)
        if tuning_result is None:
            self._reset_fsm()
            return None, 0.0

        # --- S3: LOCKED (Hysteresis & 3-Frame Stability Timer) ---
        current_string = tuning_result.string_name
        if current_string == self.last_string:
            self.consecutive_matches += 1
        else:
            self.consecutive_matches = 1
            self.last_string = current_string

        if self.consecutive_matches >= self.required_matches:
            self.state = "LOCKED"
            return tuning_result.string_name, tuning_result.cents_error

        return None, 0.0

    def _reset_fsm(self):
        """Global reset condition: returns FSM to S0 (IDLE)."""
        self.state = "IDLE"
        self.consecutive_matches = 0
        self.last_string = None
