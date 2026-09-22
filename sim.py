# sim.py
# Color preview of the 8x8 LED board in your terminal, now with an AI
# opponent, sound cues (printed as text, since a laptop has no piezo buzzer),
# and a best-of-N tournament between games.
#
# Run with:  python sim.py           (play a tournament)
#            python sim.py --colors  (check your terminal shows colors)
#
# Controls each turn (type keys, then press Enter; you can chain them,
# e.g. "ddds"):
#   a = move cursor left     d = move cursor right     s = drop piece
#   c = switch color palette q = quit
import os
import sys
import time

from game import COLS, new_board, other, drop_piece, is_full, find_winner
from display import SIZE, PALETTES, render, drop_frames
from ai import ai_move
from sound import play_cue
from tournament import new_match, record_game, is_match_over, match_summary, games_needed_to_win

os.system("")  # enables ANSI colors in Windows terminals


def screen_color(color):
    """Colors used ONLY in this preview. Real LEDs glow on their own, but on a
    screen dim colors vanish into the dark terminal background, so lift them.
    'Off' LEDs are shown as gray."""
    r, g, b = color
    peak = max(r, g, b)
    if peak == 0:
        return (55, 55, 55)
    if peak < 120:
        k = 120.0 / peak
        return (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)))
    return color


def cell(color):
    r, g, b = screen_color(color)
    return "\033[48;2;%d;%d;%dm  \033[0m" % (r, g, b)


def draw(frame, message=""):
    out = ["\033[H"]
    for y in range(SIZE):
        out.append("".join(cell(frame[y][x]) for x in range(SIZE)) + "\033[K\n")
    out.append("\033[K\n")
    out.append(message + "\033[K\n")
    out.append("a/d move, s drop, c palette, q quit\033[K\n")
    out.append("\033[J")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def color_check():
    samples = [
        ("bright red", (255, 0, 0)), ("amber", (255, 170, 0)),
        ("blue", (0, 90, 255)), ("orange", (255, 110, 0)),
        ("white", (255, 255, 255)), ("dim board blue", (0, 0, 30)),
        ("off (black)", (0, 0, 0)),
    ]
    print()
    for name, color in samples:
        print(cell(color) + cell(color) + "  " + name)
    print()


def print_tone(freq, duration):
    """Stand-in for the real speaker. A laptop has no piezo buzzer, so this
    prints the note instead. code.py replaces this with a real tone_out."""
    print("  \u266a %d Hz for %.2fs" % (freq, duration))


def choose_opponent():
    print("Choose your opponent for player 2:")
    print("  1) human   2) easy AI   3) medium AI   4) hard AI")
    choice = input("> ").strip()
    return {"1": None, "2": "easy", "3": "medium", "4": "hard"}.get(choice, None)


def choose_best_of():
    raw = input("Best of how many games? (default 3): ").strip()
    return int(raw) if raw.isdigit() and int(raw) % 2 == 1 else 3


def play_one_game(starter, ai_difficulty, pal_i, names):
    """Play one game. Returns (winner_or_None_for_draw, final_pal_i)."""
    board = new_board()
    player = starter
    cursor = COLS // 2

    while True:
        palette = PALETTES[names[pal_i]]
        is_ai_turn = ai_difficulty and player == 2

        if is_ai_turn:
            draw(render(board, cursor, player, palette),
                 "Player 2 (AI, %s) is thinking..." % ai_difficulty)
            time.sleep(0.4)
            col = ai_move(board, player, ai_difficulty)
        else:
            draw(render(board, cursor, player, palette),
                 "Player %d's turn   palette: %s" % (player, names[pal_i]))
            keys = input("> ").strip().lower()
            col = None
            for key in keys:
                if key == "a":
                    cursor = max(0, cursor - 1)
                elif key == "d":
                    cursor = min(COLS - 1, cursor + 1)
                elif key == "c":
                    pal_i = (pal_i + 1) % len(names)
                elif key == "q":
                    return "quit", pal_i
                elif key == "s":
                    col = cursor
            if col is None:
                continue

        palette = PALETTES[names[pal_i]]
        row = drop_piece(board, col, player)
        if row == -1:
            play_cue("invalid", print_tone)
            continue

        cursor = col
        for frame in drop_frames(board, col, row, player, palette):
            draw(frame)
            time.sleep(0.06)
        play_cue("drop", print_tone)

        result = find_winner(board)
        if result:
            winner, cells = result
            for i in range(8):
                draw(render(board, cursor, player, palette,
                            win_cells=cells, flash_on=(i % 2 == 0)),
                     "Player %d wins this game!" % winner)
                time.sleep(0.2)
            play_cue("win", print_tone)
            return winner, pal_i
        if is_full(board):
            draw(render(board, cursor, player, palette), "Draw.")
            play_cue("draw", print_tone)
            return None, pal_i

        player = other(player)


def main():
    names = list(PALETTES)
    pal_i = 0
    sys.stdout.write("\033[2J\033[H")

    ai_difficulty = choose_opponent()
    best_of = choose_best_of()
    match = new_match(best_of)
    play_cue("new_game", print_tone)

    while not is_match_over(match):
        print("\nGame %d. %s" % (match["games_played"] + 1, match_summary(match)))
        print("(need %d wins to take the match)" % games_needed_to_win(match))
        time.sleep(1.0)

        result, pal_i = play_one_game(match["round_starter"], ai_difficulty, pal_i, names)
        if result == "quit":
            print("Match abandoned.")
            return
        record_game(match, result)

    print("\n" + match_summary(match))


if __name__ == "__main__":
    if "--colors" in sys.argv:
        color_check()
    else:
        main()