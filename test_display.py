# test_display.py
# Run with:  python -m pytest
from game import ROWS, COLS, new_board, drop_piece, find_winner
from display import (
    SIZE, BOARD_TOP, BLACK, WHITE, BOARD_BG, PALETTES,
    dim, render, drop_frames, pixel_index, frame_to_pixels,
)

P = PALETTES["classic"]


def test_frame_is_8x8():
    frame = render(new_board(), 3, 1, P)
    assert len(frame) == SIZE
    assert all(len(row) == SIZE for row in frame)


def test_empty_board_cells_use_background():
    frame = render(new_board(), 3, 1, P)
    for r in range(ROWS):
        for c in range(COLS):
            assert frame[BOARD_TOP + r][c] == BOARD_BG


def test_spare_row_is_off():
    frame = render(new_board(), 3, 1, P)
    for x in range(COLS):
        assert frame[SIZE - 1][x] == BLACK


def test_cursor_shows_current_player_color():
    frame = render(new_board(), 4, 2, P)
    assert frame[0][4] == P[2]
    assert frame[0][3] == BLACK


def test_piece_drawn_with_row_offset():
    board = new_board()
    row = drop_piece(board, 3, 1)          # lands on board row 5
    frame = render(board, 0, 2, P)
    assert frame[BOARD_TOP + row][3] == P[1]


def test_turn_indicator_column():
    frame = render(new_board(), 0, 2, P)
    for y in range(SIZE):
        assert frame[y][SIZE - 1] == dim(P[2], 0.25)


def test_win_cells_flash_white_then_off():
    board = new_board()
    for col in range(4):
        drop_piece(board, col, 1)
    player, cells = find_winner(board)
    on = render(board, 0, 2, P, win_cells=cells, flash_on=True)
    off = render(board, 0, 2, P, win_cells=cells, flash_on=False)
    for r, c in cells:
        assert on[BOARD_TOP + r][c] == WHITE
        assert off[BOARD_TOP + r][c] == BLACK


def test_dim_scales_color():
    assert dim((200, 100, 0), 0.5) == (100, 50, 0)


def test_all_palette_values_are_valid_bytes():
    for palette in PALETTES.values():
        for color in palette.values():
            assert len(color) == 3
            assert all(isinstance(v, int) and 0 <= v <= 255 for v in color)


def test_palettes_have_distinct_player_colors():
    for palette in PALETTES.values():
        assert palette[1] != palette[2]


def test_pixel_index_straight_wiring():
    assert pixel_index(0, 0) == 0
    assert pixel_index(7, 0) == 7
    assert pixel_index(0, 1) == 8
    assert pixel_index(7, 7) == 63


def test_pixel_index_serpentine_wiring():
    assert pixel_index(0, 0, True) == 0
    assert pixel_index(7, 0, True) == 7
    assert pixel_index(0, 1, True) == 15   # odd rows run backwards
    assert pixel_index(7, 1, True) == 8


def test_frame_to_pixels_covers_all_64_leds_once():
    frame = render(new_board(), 3, 1, P)
    for serp in (False, True):
        pixels = frame_to_pixels(frame, serp)
        assert len(pixels) == 64
    # every index used exactly once
    seen = sorted(pixel_index(x, y, True) for y in range(SIZE) for x in range(SIZE))
    assert seen == list(range(64))


def test_frame_to_pixels_places_color_at_strip_index():
    board = new_board()
    row = drop_piece(board, 2, 1)
    frame = render(board, 0, 2, P)
    y = BOARD_TOP + row
    assert frame_to_pixels(frame, False)[pixel_index(2, y)] == P[1]
    assert frame_to_pixels(frame, True)[pixel_index(2, y, True)] == P[1]


def test_drop_frames_count_and_landing():
    board = new_board()
    row = drop_piece(board, 3, 1)
    frames = drop_frames(board, 3, row, 1, P)
    assert len(frames) == BOARD_TOP + row
    assert frames[-1][BOARD_TOP + row][3] == P[1]
    assert frames[0][1][3] == P[1]         # starts just under the cursor


def test_drop_frames_last_frame_matches_normal_render():
    board = new_board()
    row = drop_piece(board, 5, 2)
    frames = drop_frames(board, 5, row, 2, P)
    assert frames[-1] == render(board, 5, 2, P)