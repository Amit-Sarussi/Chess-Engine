from calendar import c
import json
from headers import *
import hashlib

scoreboard_cache = None

def load_scoreboards():
    global scoreboard_cache
    global counter
    scoreboard_cache = {}
    counter = {}
    for i in range(50):
        with open(f"{scoreboard_dir}/scoreboard_{i}.json", "r") as f:
            scoreboard_cache[f"scoreboard_{i}.json"] = json.load(f)
            
def evaluate_game(game, alpha=0.9):
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
    
    for index, fen in enumerate(relevant_positions[1:]):
        evaluations.append((fen, alpha * evaluations[index][1]))
    
    return evaluations

def update_score(position_data):
    fen, score = position_data
    filename = get_filename_from_fen(fen)
    
    scoreboard = scoreboard_cache[filename]
    
    if fen not in scoreboard:
        scoreboard[fen] = (score, 1)
    else:
        new_avg = (scoreboard[fen][0] * scoreboard[fen][1] + score) / (scoreboard[fen][1] + 1)
        scoreboard[fen] = (new_avg, scoreboard[fen][1] + 1)
    

def save_game_data(game_data):
    if scoreboard_cache == None:
        load_scoreboards()
        
    for game in game_data:
        # Evaluate the game using the chosen evaluation function
        scores = evaluate_game(game)
        # For each score look it up in the scoreboard and update it
        for position_data in scores:
            update_score(position_data)
    
    # Write back all scoreboards
    for filename in scoreboard_cache.keys():
        with open(f"{scoreboard_dir}/{filename}", "w") as f:
            json.dump(scoreboard_cache[filename], f)

def get_filename_from_fen(fen):
    hash_value = int(hashlib.md5(fen.encode()).hexdigest(), 16) % 50
    return f"scoreboard_{hash_value}.json"

def create_all_scoreboards(scoreboard_count=50):
    for i in range(scoreboard_count):
        with open(f"{scoreboard_dir}/scoreboard_{i}.json", "x") as f:
            json.dump({}, f)

def combine_scoreboards(folder_from, folder_to):
    for i in range(50):
        with open(f"{folder_from}/scoreboard_{i}.json", "r") as f:
            from_scoreboard = json.load(f)
        
        with open(f"{folder_to}/scoreboard_{i}.json", "w") as f:
            to_scoreboard = json.load(f)
            
        for key in from_scoreboard.keys():
            if key in to_scoreboard:
                before_avg = to_scoreboard[key][0]
                before_amount = to_scoreboard[key][1]
                after_amount = before_amount + from_scoreboard[key][1]
                to_scoreboard[key][0] = (before_avg * before_amount + from_scoreboard[key][0]) / after_amount
                to_scoreboard[key][1] = after_amount
            else:
                to_scoreboard[key] = from_scoreboard[key]
        
        with open(f"{folder_to}/scoreboard_{i}.json", "w") as f:
            json.dump(to_scoreboard, f)
    
#create_all_scoreboards()
