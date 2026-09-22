# tournament.py
# Best-of-N match tracking layered on top of a single game of Connect 4.
# No hardware imports, so it is testable on a laptop and also runs on
# CircuitPython.
#
# A "match" is a series of games between two players. Player numbers (1, 2)
# are the same ones game.py uses; a match just keeps score across games and
# decides who goes first each round (loser of the previous game goes first,
# which is a common house rule; the very first game alternates by round
# number so a fresh match doesn't always favor player 1).

from game import new_board


def new_match(best_of=3):
    """Start a fresh match. best_of should be odd so a winner is guaranteed
    without a tiebreaker."""
    return {
        "best_of": best_of,
        "wins": {1: 0, 2: 0},
        "games_played": 0,
        "round_starter": 1,
        "winner": None,          # set once the match is decided
        "history": [],           # list of (winner_or_None_for_draw)
    }


def games_needed_to_win(match):
    return match["best_of"] // 2 + 1


def record_game(match, result):
    """Record one finished game. result is the winning player (1 or 2), or
    None for a draw. Updates win counts, history, and next-round starter,
    and sets match['winner'] once someone has clinched the series."""
    if match["winner"] is not None:
        raise ValueError("match is already decided")

    match["games_played"] += 1
    match["history"].append(result)

    if result is None:
        # Draws don't score, but the loser-goes-first rule has no loser, so
        # simply alternate who starts the next game.
        match["round_starter"] = 2 if match["round_starter"] == 1 else 1
    else:
        match["wins"][result] += 1
        loser = 2 if result == 1 else 1
        match["round_starter"] = loser

        needed = games_needed_to_win(match)
        if match["wins"][result] >= needed:
            match["winner"] = result

    return match


def is_match_over(match):
    return match["winner"] is not None


def match_summary(match):
    """A short, display-friendly string, e.g. 'Best of 3: 2-1, Player 1 wins the match!'"""
    line = "Best of %d: %d-%d" % (match["best_of"], match["wins"][1], match["wins"][2])
    if match["winner"]:
        line += ", Player %d wins the match!" % match["winner"]
    return line


def new_game_board(match):
    """Convenience: fresh board plus who starts this round."""
    return new_board(), match["round_starter"]