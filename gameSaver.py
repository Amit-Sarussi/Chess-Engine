import sqlite3
import json
import hashlib
from headers import *  # assuming you have your game_results and other constants defined

# Initialize the SQLite database and create the table if it doesn't exist.
def init_db(db_path="scoreboard.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scoreboard (
            board TEXT PRIMARY KEY,
            avg_score REAL,
            count INTEGER
        )
    """)
    conn.commit()
    return conn

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
    
    for index, board in enumerate(relevant_positions[1:]):
        evaluations.append((board, alpha * evaluations[index][1]))
    
    return evaluations

# Update a single board evaluation in the SQLite database.
def update_score(conn, position_data):
    board, score = position_data
    cursor = conn.cursor()
    # Check if this Board already exists.
    cursor.execute("SELECT avg_score, count FROM scoreboard WHERE board=?", (board,))
    result = cursor.fetchone()
    if result is None:
        # Insert new record if not found.
        cursor.execute("INSERT INTO scoreboard (board, avg_score, count) VALUES (?, ?, ?)",
                       (board, score, 1))
    else:
        avg_score, count = result
        new_count = count + 1
        new_avg = (avg_score * count + score) / new_count
        cursor.execute("UPDATE scoreboard SET avg_score=?, count=? WHERE board=?",
                       (new_avg, new_count, board))
    # (Commit outside this function for performance.)
    

# Process and save a batch of games into the SQLite database.
def save_game_data(game_data):
    conn = init_db()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN")
        for game in game_data:
            scores = evaluate_game(game)
            for position_data in scores:
                update_score(conn, position_data)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error during batch update:", e)
    finally:
        conn.close()

    

