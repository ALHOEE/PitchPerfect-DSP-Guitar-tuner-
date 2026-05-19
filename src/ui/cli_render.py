import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class CliRenderer:
    def __init__(self):
        self.console = Console()

    def clear(self):
        """Clears the console to create a seamless frame-update effect without scrolling."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def render_tuner(self, note, deviation):
        self.clear()
        
        # Handle silent state (no signal detected)
        if not note:
            display_text = Text("\n🎸 Pluck a string... 🎸\n", style="bold cyan", justify="center")
            self.console.print(Panel(display_text, title="[bold white]PitchPerfect DSP Tuner[/]", border_style="blue"))
            return

        # Map deviation (-50 to +50 cents) to an 11-character gauge string
        pointer_pos = int((deviation + 50) / 10)  
        pointer_pos = max(0, min(10, pointer_pos))
        
        gauge = ["-"] * 11
        gauge[pointer_pos] = "🔺"
        gauge_str = "".join(gauge[:5]) + "|" + "".join(gauge[6:])

        # Determine UI status color based on tuning accuracy (<= 2 cents threshold)
        if abs(deviation) < 2:
            color = "bold green"
            status = " PERFECT! IN TUNE "
        elif deviation < 0:
            color = "bold yellow"
            status = " TOO LOW (Flat) 🎸"
        else:
            color = "bold red"
            status = " TOO HIGH (Sharp) 🎸"

        # Construct the formatted UI panel display
        text = Text()
        text.append(f"\nDetected Note: {note}\n\n", style=f"{color}
