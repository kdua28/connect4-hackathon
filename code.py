# code.py  (this is the file CircuitPython runs on the board)
#
# UNTESTED TEMPLATE. Every line marked ASSUMPTION depends on the real hardware,
# which you will learn about at the orientation call. Copy game.py, display.py
# and this file onto the CIRCUITPY drive. Depending on the board, the neopixel
# library may also need to be in the drive's lib/ folder.
import time
import board
import digitalio
import neopixel

from game import COLS, new_board, other, drop_piece, is_full, find_winner
from display import SIZE, PALETTES, render, drop_frames, frame_to_pixels

PIXEL_PIN = board.D5      # ASSUMPTION: data pin for the LED matrix
BRIGHTNESS = 0.1          # keep low: 64 LEDs at full white can draw several amps
SERPENTINE = False        # ASSUMPTION: True if odd rows are wired right-to-left
PALETTE = PALETTES["classic"]

pixels = neopixel.NeoPixel(PIXEL_PIN, SIZE * SIZE,
                           brightness=BRIGHTNESS, auto_write=False)


def make_button(pin):
    button = digitalio.DigitalInOut(pin)
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP        # pressed = False (wired to ground)
    return button


BTN_LEFT = make_button(board.D6)    # ASSUMPTION: pin numbers
BTN_RIGHT = make_button(board.D9)   # ASSUMPTION
BTN_DROP = make_button(board.D10)   # ASSUMPTION


def pressed(button):
    """True once per press, with a simple debounce."""
    if not button.value:
        time.sleep(0.05)
        while not button.value:
            pass
        return True
    return False


def show(frame):
    colors = frame_to_pixels(frame, SERPENTINE)
    for i in range(len(colors)):
        pixels[i] = colors[i]
    pixels.show()


def play():
    grid = new_board()        # named grid because "board" is the hardware module
    player = 1
    cursor = COLS // 2

    while True:
        show(render(grid, cursor, player, PALETTE))

        if pressed(BTN_LEFT):
            cursor = max(0, cursor - 1)
        elif pressed(BTN_RIGHT):
            cursor = min(COLS - 1, cursor + 1)
        elif pressed(BTN_DROP):
            row = drop_piece(grid, cursor, player)
            if row == -1:
                continue                      # column full
            for frame in drop_frames(grid, cursor, row, player, PALETTE):
                show(frame)
                time.sleep(0.07)

            result = find_winner(grid)
            if result:
                winner, cells = result
                for i in range(8):
                    show(render(grid, cursor, player, PALETTE,
                                win_cells=cells, flash_on=(i % 2 == 0)))
                    time.sleep(0.25)
                return
            if is_full(grid):
                return
            player = other(player)


while True:
    play()
    while not pressed(BTN_DROP):   # press drop to start a new game
        pass