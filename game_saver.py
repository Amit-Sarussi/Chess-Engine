from LMDB import LMDBWrapper
import random
from headers import *  # assuming you have your game_results and other constants defined

class GameSaver:
    def __init__(self, db):
        self.db = db
        self.batch_data = {}
    
    def __del__(self) -> None:
        self.db.close()
        
    def evaluate_game(self, game, alpha=0.98) -> None:
        """
        Evaluates a chess game and updates the evaluation data for each position.
        This method processes the positions of a chess game, calculates evaluations
        for each position based on the game's result and a decay factor (alpha), 
        and updates the evaluation data in the batch or database.
        """
        positions = game["positions"]
        relevant_positions = positions[2::2]
        relevant_positions.reverse()
        evaluations = []

        # Assign initial evaluation based on the game result
        if game["result"] == game_results.black:
            evaluations.append((relevant_positions[0], 1))
        elif game["result"] == game_results.black:
            return
            evaluations.append((relevant_positions[0], 0))
        else:
            return
            evaluations.append((relevant_positions[0], 0))
        
        for index, board in enumerate(relevant_positions[1:]):
            evaluations.append((board, alpha * evaluations[index][1]))

        for fen, eval_value in evaluations:
            # Get the existing evaluation from batch or DB
            if fen in self.batch_data:
                prev_eval, count = self.batch_data[fen]
            else:
                prev_eval, count = self.db.get_or_default(fen, (0.0, 0))
                # prev_eval, count = 0.0, 0

            # Update evaluation
            new_eval = (prev_eval * count + eval_value) / (count + 1)
            self.batch_data[fen] = (new_eval, count + 1)
    
    def save_scores(self) -> None:
        """
        Saves the current batch of game scores to the database.
        """
        self.db.put_batch(self.batch_data)
        self.batch_data = {}

    def save_game_data(self, game_data) -> None:
        for game in game_data:
            self.evaluate_game(game)
        self.save_scores()
