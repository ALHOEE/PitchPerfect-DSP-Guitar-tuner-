import numpy as np
from dataclasses import dataclass
from typing import Optional

@dataclass
class TuningResult:
    string_number: int
    string_name: str
    target_freq: float
    measured_freq: float
    cents_error: float
    status: str  # "FLAT", "SHARP", or "IN_TUNE"

class GuitarStringQuantizer:
    """
    Maps a raw fundamental frequency (f0) strictly to one of the 6 standard 
    guitar strings (E2, A2, D3, G3, B3, E4) using Logarithmic Nearest-Neighbor classification.
    Eliminates non-guitar chromatic notes (e.g., F#, C#, Bb).
    """

    # Standard 6-String Guitar Tuning Look-Up Table (LUT)
    GUITAR_STRINGS_LUT = [
        {"number": 6, "name": "E", "octave": 2, "freq": 82.41},
        {"number": 5, "name": "A", "octave": 2, "freq": 110.00},
        {"number": 4, "name": "D", "octave": 3, "freq": 146.83},
        {"number": 3, "name": "G", "octave": 3, "freq": 196.00},
        {"number": 2, "name": "B", "octave": 3, "freq": 246.94},
        {"number": 1, "name": "E", "octave": 4, "freq": 329.63},
    ]

    # Valid guitar fundamental frequency bandwidth (Hz)
    MIN_VALID_FREQ = 60.0
    MAX_VALID_FREQ = 420.0
    LOCK_THRESHOLD_CENTS = 3.0

    @classmethod
    def match_guitar_string(cls, f0: float) -> Optional[TuningResult]:
        """
        Quantizes the detected frequency f0 to the nearest standard guitar string
        on a logarithmic (Cents) scale.
        """
        # Band-pass sanity check: ignore sub-bass rumble or high-frequency noise
        if f0 < cls.MIN_VALID_FREQ or f0 > cls.MAX_VALID_FREQ:
            return None

        best_match = None
        min_abs_cents = float('inf')
        signed_cents_error = 0.0

        # Evaluate logarithmic distance to each of the 6 guitar strings
        for string in cls.GUITAR_STRINGS_LUT:
            target_f = string["freq"]
            # Calculate deviation in Cents: 1200 * log2(f0 / f_target)
            cents = 1200.0 * np.log2(f0 / target_f)
            
            if abs(cents) < min_abs_cents:
                min_abs_cents = abs(cents)
                signed_cents_error = cents
                best_match = string

        # Determine tuning state for UI / CLI rendering
        if abs(signed_cents_error) <= cls.LOCK_THRESHOLD_CENTS:
            status = "IN_TUNE"
        elif signed_cents_error < 0:
            status = "FLAT (Tighten String)"
        else:
            status = "SHARP (Loosen String)"

        return TuningResult(
            string_number=best_match["number"],
            string_name=f"{best_match['name']}{best_match['octave']}",
            target_freq=best_match["freq"],
            measured_freq=round(f0, 2),
            cents_error=round(signed_cents_error, 1),
            status=status
        )
