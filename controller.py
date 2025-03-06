from attacks import player_type
from game import Game


class Controller:
    def __init__(self, opponent_type: int) -> None:
        self.opponent_type = opponent_type
    
    def start(self) -> None:
        game = Game(player_type.graphics, self.opponent_type)