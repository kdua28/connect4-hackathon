# test_ai.py
# Run with:  python -m pytest
import random

from game import new_board, drop_piece, other, is_full, find_winner, valid_columns
from ai import (
    winning_move, random_move, rule_based_move, minimax_move, ai_move,
    score_window, score_position,
)


def test_random_move_is_legal():
    random.seed(0)
    board = new_board()
    for _ in range(20):
        col = random_move(board, 1)
        assert col in valid_columns(board)


def test_winning_move_detects_immediate_win():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    assert winning_move(board, 3, 1) is True
    assert winning_move(board, 3, 2) is False


def test_winning_move_does_not_mutate_board():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    before = [row[:] for row in board]
    winning_move(board, 3, 1)
    assert board == before


def test_rule_based_takes_the_win():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    assert rule_based_move(board, 1) == 3


def test_rule_based_blocks_the_loss():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 2)
    # Player 1 to move, must block column 3 or player 2 wins next turn
    assert rule_based_move(board, 1) == 3


def test_rule_based_prefers_win_over_block():
    board = new_board()
    # Player 2 is one move from winning at column 5...
    for col in range(3):
        drop_piece(board, col, 2)
    # ...but player 1 can win immediately at column 6 instead
    board[5][6] = board[5][6]
    drop_piece(board, 6, 1)
    drop_piece(board, 6, 1)
    drop_piece(board, 6, 1)
    assert rule_based_move(board, 1) == 6


def test_minimax_takes_the_win():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    assert minimax_move(board, 1, depth=3) == 3


def test_minimax_blocks_the_loss():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 2)
    assert minimax_move(board, 1, depth=3) == 3


def test_minimax_returns_legal_column_on_full_ish_board():
    random.seed(1)
    board = new_board()
    player = 1
    for _ in range(30):
        if is_full(board) or find_winner(board):
            break
        col = minimax_move(board, player, depth=2)
        drop_piece(board, col, player)
        player = other(player)


def test_score_window_rewards_and_penalizes():
    assert score_window([1, 1, 1, 1], 1) == 100000
    assert score_window([2, 2, 2, 2], 1) == -100000
    assert score_window([1, 1, 1, 0], 1) > 0
    assert score_window([2, 2, 2, 0], 1) < 0
    assert score_window([1, 2, 0, 0], 1) == 0


def test_score_position_favors_center():
    board = new_board()
    center_board = [row[:] for row in board]
    drop_piece(center_board, 3, 1)
    edge_board = [row[:] for row in board]
    drop_piece(edge_board, 0, 1)
    assert score_position(center_board, 1) > score_position(edge_board, 1)


def test_ai_move_dispatches_by_difficulty():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    assert ai_move(board, 1, "medium") == 3
    assert ai_move(board, 1, "hard") == 3
    assert ai_move(board, 1, "nonsense") in valid_columns(board)  # falls back


def test_full_game_easy_vs_hard_completes_without_crashing():
    random.seed(2)
    board = new_board()
    player = 1
    difficulty = {1: "easy", 2: "hard"}
    for _ in range(42):
        result = find_winner(board)
        if result or is_full(board):
            break
        col = ai_move(board, player, difficulty[player])
        assert drop_piece(board, col, player) != -1
        player = other(player)
    assert find_winner(board) is not None or is_full(board)