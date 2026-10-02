# 🎲 Low-Level Design: Snake and Ladders Game

A modular, extensible implementation of the classic Snake and Ladders board game.

---

## 1. Problem Statement & Extensibility Points
1. **Configurable Board Size**: Standard is $100$ cells, but should support any $N \times N$ size.
2. **Snakes & Ladders (Jumpers)**:
   - Snake: `start > end` (drops player down).
   - Ladder: `start < end` (climbs player up).
3. **Pluggable Dice**: Support 1 or more dice, fair dice, or crooked/rigged dice for testing.
4. **Players Queue**: Support 2 to $M$ players taking sequential turns.
5. **Exact Landing Rule**: To reach 100, the roll must land exactly on the finish line or remain in place.

---

## 2. Python Implementation

```python
from collections import deque
import random
from typing import Optional

class Dice:
    def __init__(self, num_dice: int = 1):
        self.num_dice = num_dice

    def roll(self) -> int:
        return sum(random.randint(1, 6) for _ in range(self.num_dice))

class Player:
    def __init__(self, player_id: str, name: str):
        self.player_id = player_id
        self.name = name
        self.position = 0

class Board:
    def __init__(self, size: int = 100):
        self.size = size
        # jumpers[start] = end (covers both snakes and ladders)
        self.jumpers: dict[int, int] = {}

    def add_snake(self, head: int, tail: int):
        if head <= tail or head >= self.size:
            raise ValueError("Snake head must be greater than tail and inside board bounds")
        self.jumpers[head] = tail

    def add_ladder(self, start: int, end: int):
        if start >= end or end > self.size:
            raise ValueError("Ladder start must be lower than end and within bounds")
        self.jumpers[start] = end

    def get_destination(self, position: int) -> int:
        # Check if landing position triggers a snake or ladder
        return self.jumpers.get(position, position)

class SnakeAndLadderGame:
    def __init__(self, board: Board, dice: Dice, players: list[Player]):
        self.board = board
        self.dice = dice
        self.players = deque(players)
        self.winner: Optional[Player] = None

    def play_turn(self) -> tuple[Player, int, int, bool]:
        """
        Executes one player's roll and position update.
        Returns: (player, roll, new_pos, won)
        """
        player = self.players[0]
        roll = self.dice.roll()
        target = player.position + roll

        # Exact landing rule: cannot exceed board size
        if target > self.board.size:
            print(f"🎲 {player.name} rolled {roll}, but needs exact roll to reach {self.board.size}. Remains at {player.position}.")
            self.players.rotate(-1)
            return player, roll, player.position, False

        # Apply snake or ladder jumper
        final_pos = self.board.get_destination(target)
        if final_pos < target:
            print(f"🐍 Oh no! {player.name} was bitten by a snake at {target}, dropped to {final_pos}!")
        elif final_pos > target:
            print(f"🪜 Yay! {player.name} climbed a ladder at {target}, advanced to {final_pos}!")
        else:
            print(f"🎲 {player.name} rolled {roll}, moved from {player.position} to {final_pos}.")

        player.position = final_pos

        if player.position == self.board.size:
            self.winner = player
            return player, roll, player.position, True

        self.players.rotate(-1)
        return player, roll, player.position, False

# --- Simulation ---
if __name__ == "__main__":
    board = Board(100)
    board.add_snake(99, 10)
    board.add_snake(65, 40)
    board.add_ladder(5, 35)
    board.add_ladder(42, 85)

    p1 = Player("p1", "Alice")
    p2 = Player("p2", "Bob")
    game = SnakeAndLadderGame(board, Dice(1), [p1, p2])

    turns = 0
    while not game.winner and turns < 100:
        game.play_turn()
        turns += 1

    if game.winner:
        print(f"🏆 {game.winner.name} won the game in {turns} turns!")
```
