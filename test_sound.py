# test_sound.py
# Run with:  python -m pytest
from sound import CUES, play_cue, silence


class FakeSpeaker:
    def __init__(self):
        self.calls = []
        self.sleeps = []

    def tone_out(self, freq, duration):
        self.calls.append((freq, duration))

    def sleep(self, seconds):
        self.sleeps.append(seconds)


def test_every_cue_is_nonempty_and_well_formed():
    assert len(CUES) > 0
    for name, notes in CUES.items():
        assert len(notes) > 0
        for freq, duration in notes:
            assert freq > 0
            assert duration > 0


def test_play_cue_sends_every_note():
    speaker = FakeSpeaker()
    play_cue("win", speaker.tone_out)
    assert speaker.calls == CUES["win"]


def test_play_cue_single_note():
    speaker = FakeSpeaker()
    play_cue("drop", speaker.tone_out)
    assert speaker.calls == [(220, 0.05)]


def test_play_cue_unknown_name_does_nothing():
    speaker = FakeSpeaker()
    play_cue("does_not_exist", speaker.tone_out)
    assert speaker.calls == []


def test_play_cue_sleeps_between_notes_when_given_sleep():
    speaker = FakeSpeaker()
    play_cue("win", speaker.tone_out, gap=0.02, sleep=speaker.sleep)
    assert len(speaker.sleeps) == len(CUES["win"]) - 1
    assert all(s == 0.02 for s in speaker.sleeps)


def test_play_cue_no_sleep_between_notes_by_default():
    speaker = FakeSpeaker()
    play_cue("win", speaker.tone_out)
    assert speaker.sleeps == []


def test_silence_sends_zero_tone():
    speaker = FakeSpeaker()
    silence(speaker.tone_out)
    assert speaker.calls == [(0, 0)]