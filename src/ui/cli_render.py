import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class CliRenderer:
    def __init__(self):
        self.console = Console()

    def clear(self):
        """ניקוי המסך ליצירת אפקט של פריים מתעדכן (בלי לגלול למטה)"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_tuner(self, note, deviation):
        self.clear()
        
        # אם אין סיגנל (שקט)
        if not note:
            display_text = Text("\n🎸 Pluck a string... 🎸\n", style="bold cyan", justify="center")
            self.console.print(Panel(display_text, title="[bold white]PitchPerfect DSP Tuner[/]", border_style="blue"))
            return

        # מיפוי הסטייה (מטווח של 50- עד 50+) למיקום על פני 11 תווים של מחוג
        pointer_pos = int((deviation + 50) / 10)  
        pointer_pos = max(0, min(10, pointer_pos))
        
        gauge = ["-"] * 11
        gauge[pointer_pos] = "🔺"
        gauge_str = "".join(gauge[:5]) + "|" + "".join(gauge[6:])

        # קביעת צבע סטטוס לפי רמת הדיוק (מתחת ל-2 סנט זה מושלם!)
        if abs(deviation) < 2:
            color = "bold green"
            status = " PERFECT! IN TUNE "
        elif deviation < 0:
            color = "bold yellow"
            status = " TOO LOW (Flat) 🎸"
        else:
            color = "bold red"
            status = " TOO HIGH (Sharp) 🎸"

        # בניית תיבת התצוגה המעוצבת
        text = Text()
        text.append(f"\nDetected Note: {note}\n\n", style=f"{color} size=20")
        text.append(f"[-50c]  {gauge_str}  [+50c]\n\n", style="white")
        text.append(f"Deviation: {deviation:+.1f} cents | Status: {status}\n", style=color)

        self.console.print(Panel(text, title="[bold white]PitchPerfect DSP Tuner[/]", border_style=color))