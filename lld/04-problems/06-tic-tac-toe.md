# 🎮 Low-Level Design: Tic-Tac-Toe Game (NxN Board)

A popular object-oriented design and machine coding interview problem testing modular game state, clean abstractions, and $O(1)$ win evaluation.

---

## 1. Problem Statement
* Design an $N \times N$ Tic-Tac-Toe game for 2 or more players.
* Support customizable pieces (e.g. `X`, `O`, `A`, `B`).
* Evaluate winning moves in $O(1)$ time rather than checking the entire grid in $O(N^2)$ or $O(N)$.
* Detect draws when all cells are filled without a winner.

---

## 2. $O(1)$ Win Condition Math
Maintain row, column, and diagonal counters for each player:
* Let Player 1 have value $+1$ and Player 2 have value $-1$.
* When a player moves at `(row, col)`:
  - Add $+1$ (or $-1$) to `rows[row]` and `cols[col]`.
  - If `row == col`, update main diagonal.
  - If `row + col == N - 1`, update anti-diagonal.
* A player wins immediately if any counter reaches $+N$ or $-N$.

---

## 3. Python Implementation

```python
from collections import deque
from enum import Enum
from typing import Optional

class PieceType(Enum):
    X = "X"
    O = "O"

class Player:
    def __init__(self, name: str, piece: PieceType):
        self.name = name
        self.piece = piece

class Board:
    def __init__(self, size: int):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def is_valid_cell(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] is None

    def place_piece(self, row: int, col: int, piece: PieceType) -> bool:
        if not self.is_valid_cell(row, col):
            return False
        self.grid[row][col] = piece
        return True

    def is_full(self) -> bool:
        return all(cell is not None for row in self.grid for cell in row)

    def print_board(self):
        for row in self.grid:
            print(" | ".join(cell.value if cell else " " for cell in row))
            print("-" * (self.size * 4 - 3))

class TicTacToeGame:
    def __init__(self, size: int, players: list[Player]):
        self.size = size
        self.board = Board(size)
        self.players = deque(players)
        
        # O(1) win verification trackers for 2-player setup
        self.rows = [0] * size
        self.cols = [0] * size
        self.diagonal = 0
        self.anti_diagonal = 0

    def make_move(self, row: int, col: int) -> tuple[bool, Optional[str]]:
        current_player = self.players[0]

        if not self.board.place_piece(row, col, current_player.piece):
            print("Invalid move! Try again.")
            return False, None

        # Value +1 for X, -1 for O
        val = 1 if current_player.piece == PieceType.X else -1
        self.rows[row] += val
        self.cols[col] += val

        if row == col:
            self.diagonal += val
        if row + col == self.size - 1:
            self.anti_diagonal += val

        # Check win condition in O(1)
        if (abs(self.rows[row]) == self.size or
            abs(self.cols[col]) == self.size or
            abs(self.diagonal) == self.size or
            abs(self.anti_diagonal) == self.size):
            return True, f"🎉 {current_player.name} won the game!"

        if self.board.is_full():
            return True, "🤝 It's a draw!"

        # Rotate turn to next player
        self.players.rotate(-1)
        return False, None

# --- Quick Test ---
if __name__ == "__main__":
    p1 = Player("Alice", PieceType.X)
    p2 = Player("Bob", PieceType.O)
    game = TicTacToeGame(3, [p1, p2])

    moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
    for r, c in moves:
        game.board.print_board()
        over, msg = game.make_move(r, c)
        if over:
            game.board.print_board()
            print(msg)
            break
```
