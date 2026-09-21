# test_game.py
# Run with:  pytest
from game import (
    ROWS, COLS, EMPTY,
    new_board, other, valid_columns, drop_piece, is_full, find_winner,
)


def test_new_board_is_empty():
    board = new_board()
    assert len(board) == ROWS
    assert all(len(row) == COLS for row in board)
    assert all(cell == EMPTY for row in board for cell in row)


def test_piece_falls_to_bottom():
    board = new_board()
    row = drop_piece(board, 3, 1)
    assert row == ROWS - 1
    assert board[ROWS - 1][3] == 1


def test_pieces_stack():
    board = new_board()
    drop_piece(board, 2, 1)
    row = drop_piece(board, 2, 2)
    assert row == ROWS - 2
    assert board[ROWS - 2][2] == 2


def test_full_column_rejects_piece():
    board = new_board()
    for i in range(ROWS):
        assert drop_piece(board, 0, 1 + i % 2) != -1
    assert drop_piece(board, 0, 1) == -1
    assert 0 not in valid_columns(board)


def test_out_of_range_column_rejected():
    board = new_board()
    assert drop_piece(board, -1, 1) == -1
    assert drop_piece(board, COLS, 1) == -1


def test_other_player():
    assert other(1) == 2
    assert other(2) == 1


def test_no_winner_on_empty_board():
    assert find_winner(new_board()) is None


def test_horizontal_win():
    board = new_board()
    for col in range(4):
        drop_piece(board, col, 1)
    player, cells = find_winner(board)
    assert player == 1
    assert sorted(cells) == [(ROWS - 1, c) for c in range(4)]


def test_vertical_win():
    board = new_board()
    for _ in range(4):
        drop_piece(board, 5, 2)
    player, cells = find_winner(board)
    assert player == 2
    assert sorted(cells) == [(ROWS - 4 + i, 5) for i in range(4)]


def test_diagonal_down_right_win():
    # Build a staircase so player 1 owns (2,0) (3,1) (4,2) (5,3)
    board = new_board()
    board[2][0] = 1
    board[3][1] = 1
    board[4][2] = 1
    board[5][3] = 1
    player, cells = find_winner(board)
    assert player == 1
    assert sorted(cells) == [(2, 0), (3, 1), (4, 2), (5, 3)]


def test_diagonal_down_left_win():
    board = new_board()
    board[2][6] = 2
    board[3][5] = 2
    board[4][4] = 2
    board[5][3] = 2
    player, cells = find_winner(board)
    assert player == 2
    assert sorted(cells) == [(2, 6), (3, 5), (4, 4), (5, 3)]


def test_three_in_a_row_is_not_a_win():
    board = new_board()
    for col in range(3):
        drop_piece(board, col, 1)
    assert find_winner(board) is None


def test_mixed_row_is_not_a_win():
    board = new_board()
    drop_piece(board, 0, 1)
    drop_piece(board, 1, 1)
    drop_piece(board, 2, 2)
    drop_piece(board, 3, 1)
    assert find_winner(board) is None


def test_wrap_around_is_not_a_win():
    # Pieces at the end of one row and the start of the next must not count
    board = new_board()
    board[4][5] = 1
    board[4][6] = 1
    board[5][0] = 1
    board[5][1] = 1
    assert find_winner(board) is None


def test_is_full_false_until_last_piece():
    board = new_board()
    assert not is_full(board)


def test_draw_board():
    # A completely full board with no four in a row
    board = [
        [2, 1, 2, 2, 1, 2, 1],
        [1, 2, 1, 1, 1, 2, 2],
        [2, 1, 2, 2, 2, 1, 1],
        [1, 2, 2, 1, 1, 1, 2],
        [2, 1, 1, 1, 2, 2, 2],
        [2, 1, 2, 2, 1, 1, 1],
    ]
    assert is_full(board)
    assert find_winner(board) is None
    assert valid_columns(board) == []