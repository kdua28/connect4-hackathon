# test_tournament.py
# Run with:  python -m pytest
import pytest

from tournament import (
    new_match, games_needed_to_win, record_game, is_match_over,
    match_summary, new_game_board,
)


def test_new_match_defaults():
    match = new_match(best_of=3)
    assert match["wins"] == {1: 0, 2: 0}
    assert match["games_played"] == 0
    assert match["winner"] is None
    assert not is_match_over(match)


def test_games_needed_to_win_best_of_3_and_5():
    assert games_needed_to_win(new_match(3)) == 2
    assert games_needed_to_win(new_match(5)) == 3


def test_record_game_increments_wins_and_history():
    match = new_match(3)
    record_game(match, 1)
    assert match["wins"][1] == 1
    assert match["games_played"] == 1
    assert match["history"] == [1]


def test_loser_starts_next_game():
    match = new_match(3)
    record_game(match, 1)   # player 1 won, so player 2 starts next
    assert match["round_starter"] == 2
    record_game(match, 2)   # player 2 won, so player 1 starts next
    assert match["round_starter"] == 1


def test_draw_alternates_starter_and_does_not_score():
    match = new_match(3)
    starter_before = match["round_starter"]
    record_game(match, None)
    assert match["wins"] == {1: 0, 2: 0}
    assert match["games_played"] == 1
    other = 2 if starter_before == 1 else 1
    assert match["round_starter"] == other


def test_match_ends_when_a_player_clinches_best_of_3():
    match = new_match(3)
    record_game(match, 1)
    assert not is_match_over(match)
    record_game(match, 1)
    assert is_match_over(match)
    assert match["winner"] == 1


def test_match_can_go_the_distance():
    match = new_match(3)
    record_game(match, 1)
    record_game(match, 2)
    assert not is_match_over(match)
    record_game(match, 1)
    assert is_match_over(match)
    assert match["winner"] == 1


def test_best_of_5_needs_three_wins():
    match = new_match(5)
    record_game(match, 1)
    record_game(match, 1)
    assert not is_match_over(match)
    record_game(match, 1)
    assert is_match_over(match)


def test_recording_after_match_over_raises():
    match = new_match(3)
    record_game(match, 1)
    record_game(match, 1)
    with pytest.raises(ValueError):
        record_game(match, 1)


def test_match_summary_format():
    match = new_match(3)
    record_game(match, 1)
    record_game(match, 1)
    summary = match_summary(match)
    assert "2-0" in summary
    assert "Player 1 wins the match" in summary


def test_new_game_board_returns_fresh_board_and_starter():
    match = new_match(3)
    board, starter = new_game_board(match)
    assert board == [[0] * 7 for _ in range(6)]
    assert starter == match["round_starter"]
    