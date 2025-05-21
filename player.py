from board import Board
from abc import ABC, abstractmethod
from headers import color

class Player(ABC):
    """
    Abstract class for a player in the game of chess.
    This class defines the basic structure and properties of a player.
    """
    def __init__(self, board: Board, color: int = color.white) -> None:
        self.color = color
        self.board = board
    
    @abstractmethod
    def make_player_move(self) -> int | None:
        """
        Abstract method to be implemented by subclasses.
        This method should handle the logic for making a move.
        Returns:
            int | None: The move made by the player, or None if no move is made.
        """
        pass
