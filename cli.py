import os
from LMDB import LMDBWrapper
from board import Board
from controller import Controller
from headers import *
from perft import perft_test
from playerSelect import PlayerSelect
from tournament import Tournament
import shlex
import multiprocessing
from typing import Tuple
import numpy as np

class CLI:
    def __init__(self):
        self.is_running = True
        self.start()
    
    def start(self):
        """Main loop for the CLI."""
        self.welcome_text()
        print("Type 'help' for a list of commands.")
        while self.is_running:
            self.process_input()
    
    def process_input(self):
        """Process user input."""
        command = input("> ")
        args = shlex.split(command)
        match args[0]:
            case "help":
                self.help()
            case "exit":
                self.end()
            case "simulate":
                self.simulate(args)
            case "play":
                self.play(args)
            case "validate":
                self.validate(args)
            case "perft":
                self.perft(args)
            case _:
                print(f"'{args[0]}' is not a recognized command.")
        print()
    
    def help(self):
        """Display help information."""
        commands = [
            ("help", "Display this help message."),
            ("play", "Play a game against a player. Usage: play"),
            ("simulate", "Simulate a tournament between two players. Usage: simulate <num_games> <player_1_type> <player_2_type>"),
            ("validate", "Validate the scoreboards. Usage: validate"),
            ("preft", "Run a perft test. Usage: perft <fen> <depth>"),
            ("exit", "Exit the program."),
        ]
        for command in commands:
            print(f"[{command[0]}] - {command[1]}")
            
    def end(self):
        """Exit the program."""
        print("Exiting.")
        self.is_running = False
    
    def play(self, args): # play
        """Start a new game."""
        # Open player select window
        player_select = PlayerSelect().select()
        Controller(player_select).start()

    
    def simulate(self, args): # simulate <num_games> <player_1_type> <player_2_type>
        """Simulate a tournament between two players."""
        if len(args) != 4:
            print("Invalid number of arguments.")
            print("Usage: simulate <num_games> <player_1_type> <player_2_type>")
            return
        
        if not args[1].isnumeric():
            print("Invalid number of games.")
            print("Usage: simulate <num_games> <player_1_type> <player_2_type>")
            return
        
        num_games = int(args[1])
        player_type_converter = {"random": player_type.random, "heuristics": player_type.heuristics, "smart": player_type.smart, "ai": player_type.ai}
        player_1_type = args[2]
        if player_1_type not in player_type_converter:
            print("Invalid player type.")
            print("player_type must be 'random', or 'heuristics'")
            return
        
        player_1_type = player_type_converter[player_1_type]
        player_2_type = args[3]
        if player_2_type not in player_type_converter:
            print("Invalid player type.")
            print("player_type must be 'random', 'heuristics', 'smart', or 'ai'")
            return
        
        player_2_type = player_type_converter[player_2_type]
        
        tournament = Tournament(player_1_type, player_2_type, num_games)
        tournament.start()
        tournament.print_results()
        
    def perft(self, args): # perft <fen> <depth>
        """Run a perft test."""
        if len(args) != 3:
            print("Invalid number of arguments.")
            print("Usage: perft <fen> <depth>")
            return
        
        starting_fen = args[1]
        if not args[2].isnumeric():
            print("Invalid depth.")
            print("Usage: perft <fen> <depth>")
            return
        
        depth = int(args[2])
    
        if not Board.validate_fen(starting_fen):
            print(f"Invalid FEN: {starting_fen}")
            return
        
        print(perft_test(starting_fen, depth))
    
    def read_chunk(self, start_idx: int, end_idx: int, db_path: str) -> Tuple[int, int, int]:
        """Worker function to read a chunk of the DB and count categories."""  # Import inside the process
        from LMDB import LMDBWrapper
        db = LMDBWrapper(db_path)
        cursor = db.env.begin().cursor()
        counter = 0
        counter3 = 0
        
        ones = zeros = betweens = 0

        for i, (key_bytes, value_bytes) in enumerate(cursor):
            if i < start_idx:
                continue
            if i >= end_idx:
                break
            
            dtype = np.dtype([('eval', np.float32), ('count', np.uint32)])
            val = np.frombuffer(value_bytes, dtype=dtype, count=1)[0]
            eval_value = val['eval']
            key = db._decode_key(key_bytes)

            if eval_value == 1.0:
                ones += 1
                if start_idx == 0 and counter < 2:
                    print(f"Key: {key} | Value: {eval_value}")
                    counter += 1
            elif eval_value == 0.0:
                zeros += 1
            elif eval_value == 0.98:
                betweens += 1
                if start_idx == 0 and counter3 < 3:
                    print(f"Key: {key} | Value: {eval_value}")
                    counter3 += 1
            else:
                betweens += 1
            

        return ones, zeros, betweens
    
    def validate(self, args):
        """Get data from the database for validation."""
        db_path = "scoreboards"
        scoreboard_file = "scoreboards/data.mdb"
        if not os.path.isfile(scoreboard_file):
            print(f"Invalid file: {scoreboard_file}")
            return

        db = LMDBWrapper(db_path)
        total_keys = db.count_keys()
        num_workers = multiprocessing.cpu_count()
        chunk_size = total_keys // num_workers

        print(f"Processing {total_keys:,} entries with {num_workers} workers")

        with multiprocessing.Pool(num_workers) as pool:
            chunks = [(i * chunk_size, (i + 1) * chunk_size if i != num_workers - 1 else total_keys)
                    for i in range(num_workers)]
            args_for_workers = [(start, end, db_path) for start, end in chunks]
            results = pool.starmap(self.read_chunk, args_for_workers)

        # Aggregate results
        ones = sum(r[0] for r in results)
        zeros = sum(r[1] for r in results)
        betweens = sum(r[2] for r in results)
        total = ones + zeros + betweens

        print(f"Ones: {ones} | Zeros: {zeros} | Betweens: {betweens} | Total: {total}")

        total_mb, available_mb = db.get_available_space()
        used = total_mb - available_mb
        print(f"Total space: {total_mb:.2f} MB, Available: {available_mb:.2f} MB, Used: {used:.2f} MB")

    def welcome_text(self):
        """Display welcome text."""
        text = """
           _____ _                     ______             _            
          / ____| |                   |  ____|           (_)           
         | |    | |__   ___  ___ ___  | |__   _ __   __ _ _ _ __   ___ 
         | |    | '_ \\ / _ \\/ __/ __| |  __| | '_ \\ / _` | | '_ \\ / _ \\
         | |____| | | |  __/\\__ \\__ \\ | |____| | | | (_| | | | | |  __/
          \\_____|_| |_|\\___||___/___/ |______|_| |_|\\__, |_|_| |_|\\___|
                             _ _      _____          __/ |           _ 
             /\\             (_) |    / ____|        |___/           (_)
            /  \\   _ __ ___  _| |_  | (___   __ _ _ __ _   _ ___ ___ _ 
           / /\\ \\ | '_ ` _ \\| | __|  \\___ \\ / _` | '__| | | / __/ __| |
          / ____ \\| | | | | | | |_   ____) | (_| | |  | |_| \\__ \\__ \\ |
         /_/    \\_\\_| |_| |_|_|\\__| |_____/ \\__,_|_|   \\__,_|___/___/_|
                
                                                                                                                      
        """
        print(text)