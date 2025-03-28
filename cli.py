import json
from math import e
import os
from LMDB import LMDBWrapper
from board import Board
from game import Game
from headers import *
from perft import perft_test
from tournament import Tournament
import shlex

class CLI:
    def __init__(self):
        self.is_running = True
        self.start()
    
    def start(self):
        self.welcome_text()
        print("Type 'help' for a list of commands.")
        while self.is_running:
            self.process_input()
    
    def process_input(self):
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
            case "validate_scoreboards":
                self.validate_scoreboards(args)
            case "perft":
                self.perft(args)
            case _:
                print(f"'{args[0]}' is not a recognized command.")
        print()
    
    def help(self):
        commands = [
            ("help", "Display this help message."),
            ("play", "Play a game against a player. Usage: play <opponent_player_type>"),
            ("simulate", "Simulate a tournament between two players. Usage: simulate <num_games> <player_1_type> <player_2_type>"),
            ("validate_scoreboards", "Validate the scoreboards. Usage: validate_scoreboards <scoreboard_dir>"),
            ("preft", "Run a perft test. Usage: perft <fen> <depth>"),
            ("exit", "Exit the program."),
        ]
        for command in commands:
            print(f"[{command[0]}] - {command[1]}")
            
    def end(self):
        print("Exiting.")
        self.is_running = False
    
    def play(self, args): # play <opponent_player_type>
        # if len(args) != 2:
        #     print("Invalid number of arguments.")
        #     print("Usage: play <opponent_player_type>")
        #     return
        
        # player_type_converter = {"random": player_type.random, "heuristics": player_type.heuristics, "hybrid": player_type.hybrid}
        # player_type = args[1]
        # if player_type not in player_type_converter:
        #     print("Invalid player type.")
        #     print("player_type must be 'random', 'heuristics', or 'hybrid'")
        #     return
        
        # player_type = player_type_converter[player_type]
        # self.controller = Controller()
        ...
    
    def simulate(self, args): # simulate <num_games> <player_1_type> <player_2_type>
        if len(args) != 4:
            print("Invalid number of arguments.")
            print("Usage: simulate <num_games> <player_1_type> <player_2_type>")
            return
        
        if not args[1].isnumeric():
            print("Invalid number of games.")
            print("Usage: simulate <num_games> <player_1_type> <player_2_type>")
            return
        
        num_games = int(args[1])
        player_type_converter = {"random": player_type.random, "heuristics": player_type.heuristics, "hybrid": player_type.hybrid}
        player_1_type = args[2]
        if player_1_type not in player_type_converter:
            print("Invalid player type.")
            print("player_type must be 'random', 'heuristics', or 'hybrid'")
            return
        
        player_1_type = player_type_converter[player_1_type]
        player_2_type = args[3]
        if player_2_type not in player_type_converter:
            print("Invalid player type.")
            print("player_type must be 'random', 'heuristics', or 'hybrid'")
            return
        
        player_2_type = player_type_converter[player_2_type]
        
        tournament = Tournament(player_1_type, player_2_type, num_games)
        tournament.start()
        tournament.print_results()
        
    def perft(self, args): # perft <fen> <depth>
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
    
    def validate_scoreboards(self, args):
        if len(args) != 2:
            print("Invalid number of arguments.")
            print("Usage: validate_scoreboards <scoreboard>")
            return
    
        scoreboard_path = args[1] + ".md"
        if not os.path.isfile(scoreboard_path):
            print(f"Invalid file: {scoreboard_path}")
            return
        
        db = LMDBWrapper("scoreboards")
        
        ones = 0
        zeros = 0
        betweens = 0
        
        
                    
        print(f"Ones: {ones} | Zeros: {zeros} | Betweens: {betweens}")
        
        total, available = db.get_available_space()
        used = total - available
        print(f"Total space: {total:.2f} MB, Available space: {available:.2f} MB, Used space: {used:.2f} MB")
        
    
    
    def welcome_text(self):
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