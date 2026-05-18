import sys
from audio.stream import AudioStream
from dsp.pitch_detector import PitchDetector
from ui.gui_render import GuiRenderer

class TunerApp:
    def __init__(self):
        self.stream = AudioStream()
        self.detector = PitchDetector()
        self.gui = GuiRenderer()

        self.stream.start()
        self.update_loop()

        self.gui.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.gui.root.mainloop()

    def update_loop(self):
        audio_data = self.stream.read()
        if audio_data:
            note, deviation = self.detector.find_pitch(audio_data)
            self.gui.update_tuner(note, deviation)
        self.gui.root.after(10, self.update_loop)

    def on_close(self):
        print("Closing stream and exiting safely...")
        self.stream.stop()
        self.gui.root.destroy()

if __name__ == "__main__":
    TunerApp()