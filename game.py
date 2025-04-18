from attacks import START_POSITION
from board import Board
from headers import *
from heuristicsPlayer import HeuristicsPlayer
from randomPlayer import RandomPlayer
from smartPlayer import SmartPlayer


class Game:
    """
    A class to represent a chess game, supporting both automated play and graphical interaction.
    """
    def __init__(self, player_1_type: int, player_2_type: int, db = None) -> None:
        self.board: Board = Board(starting_fen=START_POSITION)
        self.board_copy = self.board.copy_board()
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        self.db = db
        
        match player_1_type:
            case player_type.random:
                self.player_1 = RandomPlayer(self.board, color.white)
            case player_type.heuristics:
                self.player_1 = HeuristicsPlayer(self.board, color.white)
            case player_type.smart:
                self.player_1 = SmartPlayer(self.board, self.db, color.white)
            
            case player_type.graphics:
                self.player_1 = RandomPlayer(self.board, color.white) # He wont be played but will be used to check if any move is possible
            case _:
                print("NOT IMPLMENTED YET")
        
        match player_2_type:
            case player_type.random:
                self.player_2 = RandomPlayer(self.board, color.black)
            case player_type.heuristics:
                self.player_2 = HeuristicsPlayer(self.board, color.black)
            case player_type.graphics:
                print("PLAYER 2 CAN'T BE GRAPHICS")
            case _:
                print("NOT IMPLMENTED YET")
        
        self.results = None
        
    def reset(self):
        """
        Resets the game state to its initial configuration.

        This method restores the board to its original state using a saved copy,
        resets the game data to the starting position, and clears any game results.
        """
        self.board.restore_board(*self.board_copy)
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        self.results = None
    
    # For auto play
    def play(self):
        """
        Executes the main game loop for the chess engine.
        The game continues until a checkmate, stalemate, or the maximum move count
        (50 halfmoves) is reached. Players alternate making moves, and the game
        state is updated accordingly.
        """
        # Keep on playing until a checkmate or max move count reached
        while self.results == None and self.board.halfmove <= 50:
            
            # Players making their moves
            if self.board.turn == color.white:
                move = self.player_1.make_player_move()
            else:
                move = self.player_2.make_player_move()

            # Check if this player is in checkmate or its a stalemate
            if move == None:
                if self.board.is_king_in_check(self.board.turn):
                    self.results = game_results.black if self.board.turn == color.white else game_results.white
                else:
                    self.results = game_results.stalemate
                break
            
            self.game_data["positions"].append(self.board.to_scoreboard_array())
        
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            
        self.game_data["result"] = self.results
        return self.game_data
    
    # For graphics
    def make_move(self, move): # Is move possible, Others player move, Is game over and if so who won
        """
        Executes a move in the chess game and handles the game state updates.
        """
        if move not in self.board.generate_moves(): # If move is not possible
            return False, False, None
        
        # Make the graphics move
        graphics_move_result = self.board.make_move(move, move_type.all_moves)
        if not graphics_move_result: # If move is not possible
            return False, False, None
        
        self.game_data["positions"].append(self.board.to_scoreboard_array())
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            return True, None, self.results

        # Make the other player's move
        move_result = self.player_2.make_player_move()
        
        # Check if this player is in checkmate or its a stalemate
        if move_result == None:
            if self.board.is_king_in_check(self.board.turn):
                self.results = game_results.black if self.board.turn == color.white else game_results.white
            else:
                self.results = game_results.stalemate
            return True, None, self.results

        # Check if the graphics player have a valid move to play
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            return True, move_result, self.results

        # Check if the graphics player have a valid move to play
        board_copy = self.board.copy_board()
        graphics_move_result = self.player_1.make_player_move()
        
        if graphics_move_result == None: # If move is not possible
            if self.board.is_king_in_check(self.board.turn):
                self.results = game_results.black if self.board.turn == color.white else game_results.white
            else:
                self.results = game_results.stalemate
            return True, move_result, self.results
        else:
            self.board.restore_board(*board_copy)
        
        return True, move_result, None

        
        
        
        
        

