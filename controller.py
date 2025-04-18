from attacks import player_type
from game import Game
from graphics import Graphics

class Controller:
    """
    A class to control the flow of the chess game, including initializing the opponent type,
    starting the game, and making moves.
    """
    def __init__(self, opponent_type: int) -> None:
        match opponent_type:
            case 0:
                self.opponent_type = player_type.random
            case 1:
                self.opponent_type = player_type.heuristics
            case 2:
                self.opponent_type = player_type.smart
            case 3:
                self.opponent_type = player_type.random # Later to be AI
            case _:
                raise ValueError("Invalid opponent type")
    
    def start(self) -> None:
        """
        Initializes and starts the chess game.
        """
        self.game = Game(player_type.graphics, self.opponent_type)
        self.graphics = Graphics(self.game.board, self)
    
    def make_move(self, move):
        """
        Executes a move in the current game.
        """
        return self.game.make_move(move)

Controller(0).start()