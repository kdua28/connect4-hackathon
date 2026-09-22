# ai.py
# Three difficulty levels for a Connect 4 opponent. No hardware imports, so it
# is testable on a laptop and also runs on CircuitPython.
#
# ai_move(board, player, difficulty) returns the column to play.
import random

from game import ROWS, COLS, EMPTY, other, valid_columns, drop_piece, find_winner

CENTER_BONUS = 3           # extra weight for center-column pieces
WIN_SCORE = 100000


def _copy(board):
    return [row[:] for row in board]


def _try_move(board, col, player):
    """Simulate a move on a COPY. Returns (new_board, row) or (None, -1) if
    the column is full."""
    b = _copy(board)
    row = drop_piece(b, col, player)
    if row == -1:
        return None, -1
    return b, row


def winning_move(board, col, player):
    """True if dropping in col wins immediately for player."""
    b, row = _try_move(board, col, player)
    if row == -1:
        return False
    result = find_winner(b)
    return result is not None and result[0] == player


def random_move(board, player):
    """Easy difficulty: any legal column, chosen at random."""
    cols = valid_columns(board)
    return random.choice(cols) if cols else -1


def rule_based_move(board, player):
    """Medium difficulty:
    1. Win now if possible.
    2. Otherwise block the opponent's immediate win.
    3. Otherwise play randomly, preferring center columns."""
    cols = valid_columns(board)
    if not cols:
        return -1

    for col in cols:
        if winning_move(board, col, player):
            return col

    opponent = other(player)
    for col in cols:
        if winning_move(board, col, opponent):
            return col

    return _weighted_random(cols)


def _weighted_random(cols):
    center = COLS // 2
    weights = [max(1, 3 - abs(c - center)) for c in cols]
    return random.choices(cols, weights=weights, k=1)[0]


def score_window(cells, player):
    """Score a 4-cell window for player. Rewards near-wins, penalizes the
    opponent's near-wins, and never rewards a window that's already mixed
    or blocked."""
    opponent = other(player)
    mine = cells.count(player)
    theirs = cells.count(opponent)
    empty = cells.count(EMPTY)

    if mine == 4:
        return WIN_SCORE
    if theirs == 4:
        return -WIN_SCORE
    if mine > 0 and theirs > 0:
        return 0  # blocked window, no one can complete it

    if mine == 3 and empty == 1:
        return 50
    if mine == 2 and empty == 2:
        return 10
    if theirs == 3 and empty == 1:
        return -60   # weight slightly above our own 3s: block first
    if theirs == 2 and empty == 2:
        return -8
    return 0


def score_position(board, player):
    """Heuristic score of the whole board from player's point of view."""
    score = 0

    for row in range(ROWS):
        for col in range(COLS - 3):
            score += score_window([board[row][col + i] for i in range(4)], player)
    for col in range(COLS):
        for row in range(ROWS - 3):
            score += score_window([board[row + i][col] for i in range(4)], player)
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            score += score_window([board[row + i][col + i] for i in range(4)], player)
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            score += score_window([board[row - i][col + i] for i in range(4)], player)

    center_col = COLS // 2
    center_count = sum(1 for row in range(ROWS) if board[row][center_col] == player)
    score += center_count * CENTER_BONUS

    return score


def minimax(board, depth, alpha, beta, maximizing, player):
    """Depth-limited minimax with alpha-beta pruning.
    Returns (best_score, best_col). Scores are from `player`'s point of view."""
    cols = valid_columns(board)
    result = find_winner(board)

    if result is not None:
        winner = result[0]
        if winner == player:
            return WIN_SCORE + depth, None   # win sooner is scored higher
        return -WIN_SCORE - depth, None
    if not cols:
        return 0, None
    if depth == 0:
        return score_position(board, player), None

    mover = player if maximizing else other(player)
    best_col = cols[0]

    if maximizing:
        value = float("-inf")
        for col in cols:
            b, _ = _try_move(board, col, mover)
            score, _ = minimax(b, depth - 1, alpha, beta, False, player)
            if score > value:
                value, best_col = score, col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_col
    else:
        value = float("inf")
        for col in cols:
            b, _ = _try_move(board, col, mover)
            score, _ = minimax(b, depth - 1, alpha, beta, True, player)
            if score < value:
                value, best_col = score, col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_col


def minimax_move(board, player, depth=4):
    """Hard difficulty: win/block first (cheap and exact), then minimax for
    everything else. depth=4 is fast enough to run on a microcontroller;
    raise it on a laptop for a stronger opponent."""
    cols = valid_columns(board)
    if not cols:
        return -1
    for col in cols:
        if winning_move(board, col, player):
            return col
    opponent = other(player)
    for col in cols:
        if winning_move(board, col, opponent):
            return col

    _, col = minimax(board, depth, float("-inf"), float("inf"), True, player)
    return col if col is not None else _weighted_random(cols)


DIFFICULTIES = {
    "easy": random_move,
    "medium": rule_based_move,
    "hard": minimax_move,
}


def ai_move(board, player, difficulty="medium"):
    """Look up and run the requested difficulty. Returns a column, or -1 if
    the board is full."""
    fn = DIFFICULTIES.get(difficulty, rule_based_move)
    return fn(board, player)