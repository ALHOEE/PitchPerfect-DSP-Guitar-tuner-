import numpy as np

class PitchDetector:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        # תדרי המיתרים של גיטרה בכיוון סטנדרטי (E2, A2, D3, G3, B3, E4)
        self.GUITAR_NOTES = [
            {"note": "E2", "freq": 82.41},
            {"note": "A2", "freq": 110.00},
            {"note": "D3", "freq": 146.83},
            {"note": "G3", "freq": 196.00},
            {"note": "B3", "freq": 246.94},
            {"note": "E4", "freq": 329.63}
        ]

    def find_pitch(self, audio_data):
        """מציאת תדר היסוד באמצעות Autocorrelation"""
        signal = np.frombuffer(audio_data, dtype=np.int16)
        
        # נרמול האות ובדיקה שאין שקט מוחלט
        if np.max(np.abs(signal)) < 500:  
            return None, 0.0

        # חישוב מתאם עצמי (Autocorrelation)
        corr = np.correlate(signal, signal, mode='full')
        corr = corr[len(corr)//2:]

        # מציאת נקודת השיא הראשונה אחרי ה-Zero-lag
        d = np.diff(corr)
        start = np.where(d > 0)[0]
        if len(start) == 0:
            return None, 0.0
        peak = start[0] + np.argmax(corr[start[0]:])

        if peak == 0:
            return None, 0.0

        # המרת מיקום השיא לתדר (Hz)
        frequency = self.sample_rate / peak
        
        # סינון רעשי רקע מחוץ לטווח הגיטרה הרלוונטי
        if frequency < 50 or frequency > 400:
            return None, 0.0

        return self._match_note(frequency)

    def _match_note(self, frequency):
        """התאמת התדר לתו הקרוב ביותר וחישוב הסטייה"""
        closest_note = min(self.GUITAR_NOTES, key=lambda x: abs(x["freq"] - frequency))
        # חישוב סטייה בסנטים (Cents deviation) למדידת דיוק הכיוון
        deviation = 1200 * np.log2(frequency / closest_note["freq"])
        return closest_note["note"], deviation