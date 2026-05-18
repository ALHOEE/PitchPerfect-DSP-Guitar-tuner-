import sounddevice as sd
import numpy as np

class AudioStream:
    def __init__(self, sample_rate=44100, chunk_size=4096):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.stream = None

    def start(self):
        """פתיחת ערוץ הקלט באמצעות sounddevice המודרנית"""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.chunk_size
        )
        self.stream.start()

    def read(self):
        """קריאת חתיכת מידע והמרתה ל-bytes בשביל תאימות מלאה למוח ה-DSP"""
        if self.stream:
            # קריאת דגימות האודיו כמערך נומרי
            data, overflow = self.stream.read(self.chunk_size)
            # המרה לפורמט בייטים גולמי כדי ששאר הפרויקט יעבוד בלי לשנות שורת קוד אחת!
            return data.tobytes()
        return None

    def stop(self):
        """סגירה נקייה של הסטרים"""
        if self.stream:
            self.stream.stop()
            self.stream.close()