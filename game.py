# game.py
# Pure Connect 4 logic. No hardware imports on purpose:
#   - it can be tested on any laptop with pytest
#   - it also runs on CircuitPython (plain lists and ints only)
#
# Board layout: board[row][col], row 0 is the TOP, row ROWS-1 is the BOTTOM.
# Cells hold EMPTY (0), or a player number (1 or 2).

ROWS = 6
COLS = 7
EMPTY = 0

# The four line directions to check: right, down, down-right, down-left
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


def new_board():
    """Return a fresh empty board."""
    return [[EMPTY] * COLS for _ in range(ROWS)]


def other(player):
    """Return the opponent of player (1 <-> 2)."""
    return 2 if player == 1 else 1


def valid_columns(board):
    """Columns that still have room for a piece."""
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def drop_piece(board, col, player):
    """Drop a piece into col. Returns the row it landed in, or -1 if the
    column is out of range or full. Modifies board in place."""
    if col < 0 or col >= COLS:
        return -1
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row
    return -1


def is_full(board):
    """True when no more moves are possible."""
    return len(valid_columns(board)) == 0


def find_winner(board):
    """If someone has four in a row, return (player, cells) where cells is
    a list of the four (row, col) positions. Otherwise return None.
    The cell list is handy for a win animation later."""
    for row in range(ROWS):
        for col in range(COLS):
            player = board[row][col]
            if player == EMPTY:
                continue
            for d_row, d_col in DIRECTIONS:
                cells = [(row + i * d_row, col + i * d_col) for i in range(4)]
                if _all_owned(board, cells, player):
                    return player, cells
    return None


def _all_owned(board, cells, player):
    for r, c in cells:
        if r < 0 or r >= ROWS or c < 0 or c >= COLS:
            return False
        if board[r][c] != player:
            return False
    return True