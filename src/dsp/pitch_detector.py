import numpy as np

class PitchDetector:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # Standard guitar string frequencies (E2, A2, D3, G3, B3, E4)
        self.GUITAR_NOTES = [
            {"note": "E2", "freq": 82.41},
            {"note": "A2", "freq": 110.00},
            {"note": "D3", "freq": 146.83},
            {"note": "G3", "freq": 196.00},
            {"note": "B3", "freq": 246.94},
            {"note": "E4", "freq": 329.63}
        ]

    def find_pitch(self, audio_data):
        """Calculates the fundamental frequency using the Autocorrelation method."""
        signal = np.frombuffer(audio_data, dtype=np.int16)
        
        # Noise gate: ignore absolute silence and background noise
        if np.max(np.abs(signal)) < 500:  
            return None, 0.0

        # Compute the autocorrelation function
        corr = np.correlate(signal, signal, mode='full')
        corr = corr[len(corr)//2:]

        # Find the first prominent peak after the zero-lag region
        d = np.diff(corr)
        start = np.where(d > 0)[0]
        if len(start) == 0:
            return None, 0.0
        peak = start[0] + np.argmax(corr[start[0]:])

        if peak == 0:
            return None, 0.0

        # Convert the peak index to frequency (Hz)
        frequency = self.sample_rate / peak
        
        # Filter out frequencies outside the standard guitar range
        if frequency < 50 or frequency > 400:
            return None, 0.0

        return self._match_note(frequency)

    def _match_note(self, frequency):
        """Matches the frequency to the closest musical note and calculates the deviation."""
        closest_note = min(self.GUITAR_NOTES, key=lambda x: abs(x["freq"] - frequency))
        # Calculate pitch deviation in Cents for tuning accuracy
        deviation = 1200 * np.log2(frequency / closest_note["freq"])
        return closest_note["note"], deviation
