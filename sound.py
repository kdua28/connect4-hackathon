# sound.py
# Sound cues as plain data: (frequency_hz, duration_seconds) tones, or a
# short list of them for a sequence. No hardware imports, so this file
# is testable on a laptop and also runs on CircuitPython.
#
# On the actual board, a cue is played through a `tone_out(freq, duration)`
# function that you supply. That indirection is what makes this testable:
# tests pass in a fake tone_out that just records calls, and code.py will
# pass in a real one (see the ASSUMPTION note near the bottom).

CUES = {
    "move": [(440, 0.03)],                              # A4, short click
    "drop": [(220, 0.05)],                               # A3, low thunk
    "invalid": [(150, 0.08)],                             # low buzz
    "win": [(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.25)],  # C-E-G-C rising
    "draw": [(300, 0.15), (250, 0.25)],                    # descending, flat
    "new_game": [(392, 0.08), (523, 0.08), (659, 0.15)],   # G-C-E, upbeat
}


def play_cue(name, tone_out, gap=0.02, sleep=None):
    """Play a named cue through tone_out(freq, duration).
    sleep: a callable like time.sleep, used for the gap between notes.
    Pass sleep=None (the default) to play notes back to back with no gap,
    which is what a test double typically wants."""
    notes = CUES.get(name)
    if not notes:
        return
    for i, (freq, duration) in enumerate(notes):
        tone_out(freq, duration)
        if sleep and i < len(notes) - 1:
            sleep(gap)


def silence(tone_out):
    """Convenience for turning off a tone if your tone_out supports freq=0."""
    tone_out(0, 0)