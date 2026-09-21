# play.py
# Terminal version of Connect 4 so you can try the logic without the LED board.
# Run with:  python play.py
from game import (
    COLS, new_board, other, drop_piece, is_full, find_winner,
)

SYMBOLS = {0: ".", 1: "X", 2: "O"}


def show(board):
    print()
    for row in board:
        print(" ".join(SYMBOLS[cell] for cell in row))
    print(" ".join(str(c + 1) for c in range(COLS)))
    print()


def main():
    board = new_board()
    player = 1
    while True:
        show(board)
        raw = input("Player %d (%s), pick column 1-%d: " % (player, SYMBOLS[player], COLS))
        if not raw.strip().isdigit():
            print("Enter a number.")
            continue
        row = drop_piece(board, int(raw) - 1, player)
        if row == -1:
            print("That column is full or out of range.")
            continue
        result = find_winner(board)
        if result:
            show(board)
            print("Player %d wins!" % result[0])
            return
        if is_full(board):
            show(board)
            print("Draw.")
            return
        player = other(player)


if __name__ == "__main__":
    main()