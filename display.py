# display.py
# Turns a Connect 4 board into an 8x8 grid of RGB colors.
# No hardware imports, so it is testable on a laptop and also runs on CircuitPython.
#
# 8x8 layout (x = column 0..7 left to right, y = row 0..7 top to bottom):
#   y = 0        cursor row: shows the current player's color above the chosen column
#   y = 1..6     the 6 board rows (board row 0 is y = 1)
#   y = 7        spare row (off)
#   x = 0..6     the 7 board columns
#   x = 7        turn indicator: whole column glows dimly in the current player's color
#
# ASSUMPTION: the real board is RGB (e.g. NeoPixel style). If it is single-color,
# players will need to be told apart by brightness or blinking instead.

from game import ROWS, COLS, EMPTY

SIZE = 8
BOARD_TOP = 1          # LED row where board row 0 is drawn

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BOARD_BG = (0, 0, 30)  # empty cell: faint blue so the grid is visible

PALETTES = {
    "classic": {1: (255, 0, 0), 2: (255, 170, 0)},       # red vs amber
    "colorblind": {1: (0, 90, 255), 2: (255, 110, 0)},   # blue vs orange
}


def dim(color, factor):
    """Scale a color's brightness, e.g. dim(RED, 0.25)."""
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


def new_frame(color=BLACK):
    """An 8x8 grid indexed frame[y][x], filled with one color."""
    return [[color] * SIZE for _ in range(SIZE)]


def render(board, cursor_col, player, palette, win_cells=None, flash_on=True):
    """Build one 8x8 frame for the current game state.
    win_cells: list of (row, col) board positions to flash (from find_winner).
    flash_on: alternate True/False between frames to make the win cells blink."""
    frame = new_frame()

    # Board cells
    for r in range(ROWS):
        for c in range(COLS):
            cell = board[r][c]
            frame[BOARD_TOP + r][c] = palette[cell] if cell != EMPTY else BOARD_BG

    # Cursor row
    frame[0][cursor_col] = palette[player]

    # Turn indicator column
    glow = dim(palette[player], 0.25)
    for y in range(SIZE):
        frame[y][SIZE - 1] = glow

    # Win flash
    if win_cells:
        for r, c in win_cells:
            frame[BOARD_TOP + r][c] = WHITE if flash_on else BLACK

    return frame


def drop_frames(board, col, row, player, palette):
    """Frames of a piece falling into place. Call AFTER drop_piece, passing the
    row it returned. Returns a list of frames; the final resting position is
    the last frame (identical to a normal render)."""
    before = [line[:] for line in board]
    before[row][col] = EMPTY
    landing_y = BOARD_TOP + row
    frames = []
    for y in range(1, landing_y + 1):
        frame = render(before, col, player, palette)
        frame[y][col] = palette[player]
        frames.append(frame)
    return frames


def pixel_index(x, y, serpentine=False):
    """Position of LED (x, y) along the physical strip.
    Most 8x8 NeoPixel matrices are wired as one long strip. Some run every row
    left-to-right (serpentine=False), others zig-zag (serpentine=True)."""
    if serpentine and y % 2 == 1:
        return y * SIZE + (SIZE - 1 - x)
    return y * SIZE + x


def frame_to_pixels(frame, serpentine=False):
    """Flatten a frame into a list of 64 colors in strip order."""
    pixels = [BLACK] * (SIZE * SIZE)
    for y in range(SIZE):
        for x in range(SIZE):
            pixels[pixel_index(x, y, serpentine)] = frame[y][x]
    return pixels