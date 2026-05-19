import tkinter as tk
import math

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

class GuiRenderer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PitchPerfect DSP Guitar Tuner")
        self.root.geometry("500x450")
        self.root.configure(bg="#11111b")
        self.root.resizable(False, False)

        self.eng_title = tk.Label(
            self.root, text="PITCHPERFECT DSP ENGINE v2.0", 
            font=("Consolas", 10, "bold"), fg="#a6adc8", bg="#11111b"
        )
        self.eng_title.pack(pady=(15, 0))

        self.main_title = tk.Label(
            self.root, text="Guitar Tuner", 
            font=("Segoe UI", 20, "bold"), fg="#cdd6f4", bg="#11111b"
        )
        self.main_title.pack(pady=(0, 10))

        self.note_label = tk.Label(
            self.root, text="--", 
            font=("Segoe UI", 42, "bold"), fg="#89b4fa", bg="#11111b"
        )
        self.note_label.pack(pady=5)

        self.canvas = tk.Canvas(self.root, width=460, height=200, bg="#11111b", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.cx, self.cy = 230, 190
        self.radius = 140

        self.canvas.create_arc(
            self.cx - self.radius, self.cy - self.radius,
            self.cx + self.radius, self.cy + self.radius,
            start=30, extent=120, style=tk.ARC, outline="#313244", width=5
        )

        self._draw_marker(30, "+50c", "#f38ba8")   
        self._draw_marker(90, "0", "#a6e3a1")      
        self._draw_marker(150, "-50c", "#f9e2af")  

        self.guitar_neck = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy - self.radius, 
            fill="#b57614", width=12, capstyle=tk.PROJECTING
        )
        
        self.fretboard = self.canvas.create_line(
            self.cx, self.cy, self.cx, self.cy - self.radius, 
            fill="#3c3836", width=6
        )

        self.headstock = self.canvas.create_rectangle(
            self.cx - 10, self.cy - self.radius - 15,
            self.cx + 10, self.cy - self.radius,
            fill="#282828", outline="#b57614", width=2
        )
        
        self.status_label = tk.Label(
            self.root, text="Pluck a string to begin", 
            font=("Segoe UI", 11, "italic"), fg="#a6adc8", bg="#11111b"
        )
        self.status_label.pack(pady=10)

    def _draw_marker(self, angle_deg, label, color):
        angle_rad = math.radians(angle_deg)
        x1 = self.cx + (self.radius - 8) * math.cos(angle_rad)
        y1 = self.cy - (self.radius - 8) * math.sin(angle_rad)
        x2 = self.cx + (self.radius + 8) * math.cos(angle_rad)
        y2 = self.cy - (self.radius + 8) * math.sin(angle_rad)
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3)
        
        xt = self.cx + (self.radius + 22) * math.cos(angle_rad)
        yt = self.cy - (self.radius + 22) * math.sin(angle_rad)
        self.canvas.create_text(xt, yt, text=label, fill="#a6adc8", font=("Consolas", 10, "bold"))

    def update_tuner(self, note, deviation):
        if not note:
            self.note_label.config(text="--", fg="#89b4fa")
            self.status_label.config(text="Ready and listening...", fg="#a6adc8")
            self._move_guitar_needle(90)
            return

        # Display the raw note (e.g., E2, A2) which is the standard convention
        self.note_label.config(text=note)

        clamped_dev = max(-50, min(50, deviation))
        angle_deg = 90 - (clamped_dev * 1.2)
        self._move_guitar_needle(angle_deg)

        if abs(deviation) < 3:
            self.note_label.config(fg="#a6e3a1") 
            self.status_label.config(text=f"Perfect! ({deviation:+.1f} cents)", fg="#a6e3a1")
        elif deviation < 0:
            self.note_label.config(fg="#f9e2af") 
            self.status_label.config(text=f"Too Low ({deviation:+.1f} cents)", fg="#f9e2af")
        else:
            self.note_label.config(fg="#f38ba8") 
            self.status_label.config(text=f"Too High ({deviation:+.1f} cents)", fg="#f38ba8")

    def _move_guitar_needle(self, angle_deg):
        angle_rad = math.radians(angle_deg)
        x_end = self.cx + self.radius * math.cos(angle_rad)
        y_end = self.cy - self.radius * math.sin(angle_rad)
        
        self.canvas.coords(self.guitar_neck, self.cx, self.cy, x_end, y_end)
        self.canvas.coords(self.fretboard, self.cx, self.cy, x_end, y_end)
        
        hw, hh = 12, 16 
        hx = self.cx + (self.radius + 8) * math.cos(angle_rad)
        hy = self.cy - (self.radius + 8) * math.sin(angle_rad)
        self.canvas.coords(self.headstock, hx - hw, hy - hh, hx + hw, hy + hh)
