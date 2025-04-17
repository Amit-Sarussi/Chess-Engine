from LMDB import LMDBWrapper
from game import Game
from gameSaver import GameSaver
from headers import *

class Tournament:
    def __init__(self, player_1_type: int, player_2_type: int, num_games: int = 1):
        self.num_games = num_games
        self.games_data = []
        self.results = {"player_1": 0, "player_2": 0, "draw": 0}
        self.db = LMDBWrapper("scoreboards")
        self.game = Game(player_1_type, player_2_type, self.db)
        self.gameSaver = GameSaver(self.db)
        self.save_interval = 100_000
                
    def start(self):
        for i in range(self.num_games):
            result = self.game.play()
            self.games_data.append(result)
            match result["result"]:
                case game_results.white:
                    self.results["player_1"] += 1
                case game_results.black:
                    self.results["player_2"] += 1
                case game_results.stalemate:
                    self.results["draw"] += 1
            self.game.reset()
            
            if (i + 1) % self.save_interval == 0:
                print(f"Finished {format(i + 1, ',d')} games out of {format(self.num_games, ',d')}")
                self.gameSaver.save_game_data(self.games_data)
                self.games_data = []
                percent_complete = (i + 1) / self.num_games * 100
                print(f"Saved the last {self.save_interval} games, {percent_complete:.2f}% complete")
            elif (i + 1) % 100 == 0:
                print(f"Finished {format(i + 1, ',d')} games out of {format(self.num_games, ',d')}")
            
    def print_results(self):
        win_rate_1 = self.results["player_1"] / self.num_games * 100
        win_rate_2 = self.results["player_2"] / self.num_games * 100
        draw_rate = self.results["draw"] / self.num_games * 100
        print(f"\n{self.num_games} games were played.")
        print(f"{self.results["player_1"]} ({win_rate_1:.2f}%) wins for Player 1")
        print(f"{self.results["player_2"]} ({win_rate_2:.2f}%) wins for Player 2")
        print(f"{self.results["draw"]} ({draw_rate:.2f}%) draws.\n")

