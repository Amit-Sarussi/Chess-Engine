import json
from headers import *
import hashlib

scoreboard_cache = {}

def evaluate_game(game, alpha=0.9):
    positions = game["positions"]
    relevant_positions = positions[1::2]
    evaluations = []
    if game["result"] == game_results.white:
        evaluations.append((relevant_positions[0], 1))
    elif game["result"] == game_results.black:
        evaluations.append((relevant_positions[0], 0))
    else:
        evaluations.append((relevant_positions[0], 0.3))
    
    for index, fen in enumerate(relevant_positions[1:]):
        evaluations.append((fen, alpha * evaluations[index-1][1]))
    
    return evaluations

def update_score(position_data):
    fen, score = position_data
    filename = get_filename_from_fen(fen)
    
    if filename not in scoreboard_cache:
        with open(f"{scoreboard_dir}/{filename}", "r") as f:
            scoreboard_cache[filename] = json.load(f)
    
    scoreboard = scoreboard_cache[filename]
    
    if fen not in scoreboard:
        scoreboard[fen] = (score, 1)
    else:
        new_avg = (scoreboard[fen][0] * scoreboard[fen][1] + score) / (scoreboard[fen][1] + 1)
        scoreboard[fen] = (new_avg, scoreboard[fen][1] + 1)

    # Only write back every 1000 updates
    if len(scoreboard) % 10000 == 0:
        with open(f"{scoreboard_dir}/{filename}", "w") as f:
            json.dump(scoreboard, f)

def save_game_data(game_data):
    for game in game_data:
        # Evaluate the game using the chosen evaluation function
        scores = evaluate_game(game)
        # For each score look it up in the scoreboard and update it
        for position_data in scores:
            update_score(position_data)

def get_filename_from_fen(fen):
    hash_value = int(hashlib.md5(fen.encode()).hexdigest(), 16) % 50
    return f"scoreboard_{hash_value}.json"

def create_all_scoreboards(scoreboard_count=50):
    for i in range(scoreboard_count):
        with open(f"{scoreboard_dir}/scoreboard_{i}.json", "x") as f:
            json.dump({}, f)

