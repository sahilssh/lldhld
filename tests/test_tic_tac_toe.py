import unittest
from collections import deque
from enum import Enum

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

    def place_piece(self, row: int, col: int, piece: PieceType) -> bool:
        if self.grid[row][col] is not None:
            return False
        self.grid[row][col] = piece
        return True

class TicTacToeGame:
    def __init__(self, size: int, players: list[Player]):
        self.size = size
        self.board = Board(size)
        self.players = deque(players)
        self.rows = [0] * size
        self.cols = [0] * size
        self.diagonal = 0
        self.anti_diagonal = 0

    def make_move(self, row: int, col: int) -> tuple[bool, str]:
        current_player = self.players[0]
        if not self.board.place_piece(row, col, current_player.piece):
            return False, "Invalid"

        val = 1 if current_player.piece == PieceType.X else -1
        self.rows[row] += val
        self.cols[col] += val
        if row == col:
            self.diagonal += val
        if row + col == self.size - 1:
            self.anti_diagonal += val

        if (abs(self.rows[row]) == self.size or
            abs(self.cols[col]) == self.size or
            abs(self.diagonal) == self.size or
            abs(self.anti_diagonal) == self.size):
            return True, f"{current_player.name} won"

        self.players.rotate(-1)
        return False, "Next"

class TestTicTacToe(unittest.TestCase):
    def test_win_detection(self):
        p1 = Player("P1", PieceType.X)
        p2 = Player("P2", PieceType.O)
        game = TicTacToeGame(3, [p1, p2])

        # Moves: (0,0)[X], (1,0)[O], (0,1)[X], (1,1)[O], (0,2)[X] -> X wins row 0
        self.assertFalse(game.make_move(0, 0)[0])
        self.assertFalse(game.make_move(1, 0)[0])
        self.assertFalse(game.make_move(0, 1)[0])
        self.assertFalse(game.make_move(1, 1)[0])
        won, msg = game.make_move(0, 2)
        self.assertTrue(won)
        self.assertEqual(msg, "P1 won")

if __name__ == "__main__":
    unittest.main()
