import random
from board import Board
from player import Player
from headers import *

class RandomPlayer(Player):
    """
    RandomPlayer is a subclass of Player that represents a chess player
    making random moves on the board.
    """
    def __init__(self, board: Board, color: int = color.white) -> None:
        super().__init__(board, color)

    def make_player_move(self) -> int | None:
        """Executes a random move for the player on the chessboard."""
        all_moves = self.board.generate_moves()

        while len(all_moves) != 0:
            move = random.choice(all_moves)
            status = self.board.make_move(move)
            if status:
                return move
            else:
                all_moves.remove(move)
        return None