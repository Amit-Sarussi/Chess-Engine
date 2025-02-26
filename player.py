from board import Board
from abc import ABC, abstractmethod
from headers import color

class Player(ABC):
    def __init__(self, board: Board, color: int = color.white) -> None:
        self.color = color
        self.board = board
    
    @abstractmethod
    def make_player_move(self):
        pass
