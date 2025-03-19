from headers import *
from sql import SQL  # assuming you have your game_results and other constants defined

class GameSaver:
    def __init__(self):
        self.db = SQL("scoreboard.db")
        self.batch_data = {}
        
    def evaluate_game(self, game, alpha=0.9):
        positions = game["positions"]
        relevant_positions = positions[1::2]
        relevant_positions.reverse()
        evaluations = []
        if game["result"] == game_results.white:
            evaluations.append((relevant_positions[0], 1))
        elif game["result"] == game_results.black:
            evaluations.append((relevant_positions[0], 0))
        else:
            evaluations.append((relevant_positions[0], 0.3))
        
        for index, board in enumerate(relevant_positions[1:]):
            evaluations.append((board, alpha * evaluations[index][1]))
        
        for fen, score in evaluations:
            if fen in self.batch_data:
                avg_score, count = self.batch_data[fen]
                self.batch_data[fen] = ((avg_score * count + score) / (count + 1), count + 1)
            else:
                self.batch_data[fen] = (score, 1)


    def update_scores(self):
        for board, score_and_count in self.batch_data.items():
            # Check if this Board already exists.
            self.db.execute("SELECT avg_score, count FROM scoreboard WHERE board=?", (board,))
            result = self.db.fetchone()
            if result is None:
                # Insert new record if not found.
                self.db.execute("INSERT INTO scoreboard (board, avg_score, count) VALUES (?, ?, ?)",
                            (board, score_and_count[0], 1))
            else:
                avg_score, count = result
                new_count = count + score_and_count[1]
                new_avg = (avg_score * count + score_and_count[0]) / new_count
                self.db.execute("UPDATE scoreboard SET avg_score=?, count=? WHERE board=?",
                            (new_avg, new_count, board))
            # (Commit outside this function for performance.)

        self.batch_data = {}
        

    # Process and save a batch of games into the SQLite database.
    def save_game_data(self, game_data):
        if self.db.cursor:
            try:
                self.db.execute("BEGIN")
                for game in game_data:
                    self.evaluate_game(game)

                self.update_scores()
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                print("Error during batch update:", e)
            finally:
                self.db.disconnect()

    

