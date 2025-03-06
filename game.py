from attacks import START_POSITION
from board import Board
from headers import *
from heuristicsPlayer import HeuristicsPlayer
from hybridPlayer import HybridPlayer
from randomPlayer import RandomPlayer


class Game:
    def __init__(self, player_1_type: int, player_2_type: int) -> None:
        self.board: Board = Board(starting_fen=START_POSITION)
        self.board_copy = self.board.copy_board()
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        
        match player_1_type:
            case player_type.random:
                self.player_1 = RandomPlayer(self.board, color.white)
            case player_type.heuristics:
                self.player_1 = HeuristicsPlayer(self.board, color.white)
            case player_type.hybrid:
                self.player_1 = HybridPlayer(self.board, color.white)
            case player_type.graphics:
                print("NOT IMPLMENTED YET")
            case _:
                print("NOT IMPLMENTED YET")
        
        match player_2_type:
            case player_type.random:
                self.player_2 = RandomPlayer(self.board, color.black)
            case player_type.heuristics:
                self.player_2 = HeuristicsPlayer(self.board, color.black)
            case player_type.hybrid:
                self.player_1 = HybridPlayer(self.board, color.black)
            case player_type.graphics:
                print("INVALID TYPE")
            case _:
                print("NOT IMPLMENTED YET")
        
        self.results = None
        
    def reset(self):
        self.board.restore_board(*self.board_copy)
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        self.results = None
        
    
    def play(self):
        # Keep on playing until a checkmate or max move count reached
        while self.results == None and self.board.halfmove <= 50:
            
            # Players making their moves
            if self.board.turn == color.white:
                move = self.player_1.make_player_move()
            else:
                move = self.player_2.make_player_move()

            # Check if this player is in checkmate
            if move == None:
                if self.board.is_king_in_check(self.board.turn):
                    self.results = game_results.black if self.board.turn == color.white else game_results.white
                else:
                    self.results = game_results.stalemate
                break
            
            self.game_data["positions"].append(self.board.to_scoreboard_fen())
        
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            
        self.game_data["result"] = self.results
        return self.game_data

