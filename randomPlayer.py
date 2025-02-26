import random
from board import Board
from player import Player
from headers import *

class RandomPlayer(Player):
    def __init__(self, board: Board, color: int = color.white) -> None:
        super().__init__(board, color)

    def make_player_move(self):
        all_moves = self.board.generate_moves()

        while len(all_moves) != 0:
            move = random.choice(all_moves)
            status = self.board.make_move(move, move_type.all_moves)
            if status:
                return move
            else:
                all_moves.remove(move)
        return None