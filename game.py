import pygame
from ai_player import AIPlayer
from attacks import START_POSITION
from board import Board
from headers import *
from heuristics_player import HeuristicsPlayer
from move import get_move_capture
from random_player import RandomPlayer
from smart_player import SmartPlayer


class Game:
    """
    A class to represent a chess game, supporting both automated play and graphical interaction.
    """
    def __init__(self, player_1_type: int, player_2_type: int, db, model) -> None:
        self.board: Board = Board(starting_fen=START_POSITION)
        self.board_copy = self.board.copy_board()
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        self.db = db
        self.model = model
        self.play_sound = None
        self.results = None
        
        # Set the player types
        self.player_1 = None
        self.player_2 = None
        
        # Initialize players based on their types
        self.init_players(player_1_type, player_2_type)
        
    def init_players(self, player_1_type: int, player_2_type: int) -> None:
        """
        Initializes the players based on their types.
        """
        match player_1_type:
            case player_type.random:
                self.player_1 = RandomPlayer(self.board, color.white)
            case player_type.heuristics:
                self.player_1 = HeuristicsPlayer(self.board, color.white)
            case player_type.smart:
                print("PLAYER 1 CAN'T BE SMART")
            
            case player_type.graphics:
                self.player_1 = RandomPlayer(self.board, color.white) # He wont be played but will be used to check if any move is possible
            case _:
                print("NOT IMPLMENTED")
        
        match player_2_type:
            case player_type.random:
                self.player_2 = RandomPlayer(self.board, color.black)
            case player_type.heuristics:
                self.player_2 = HeuristicsPlayer(self.board, color.black)
            case player_type.smart:
                self.player_2 = SmartPlayer(self.board, self.db, color.black)
            case player_type.ai:
                self.player_2 = AIPlayer(self.board, self.model, color.black)
            case player_type.graphics:
                print("PLAYER 2 CAN'T BE GRAPHICS")
            case _:
                print("NOT IMPLMENTED")
        
    def reset(self) -> None:
        """
        Resets the game state to its initial configuration.

        This method restores the board to its original state using a saved copy,
        resets the game data to the starting position, and clears any game results.
        """
        self.board.restore_board(*self.board_copy)
        self.game_data = {"start_fen": START_POSITION, "positions": [START_POSITION]}
        self.results = None
    
    # For auto play
    def play(self) -> dict[str, list[str] | str]:
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
    def make_move(self, move) -> tuple[bool, int | None, int | None]:
        """
        Executes a move in the chess game and handles the game state updates.
        Returns a tuple indicating (whether the move was successful, the other player's move,
        and the game result if applicable.)
        """
        if move not in self.board.generate_moves(): # If move is not possible
            return False, False, None
        
        # Make the graphics move
        graphics_move_result = self.board.make_move(move)
        if not graphics_move_result: # If move is not possible
            return False, False, None
        
        self.game_data["positions"].append(self.board.to_scoreboard_array())
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            self.play_sound("game-end")
            return True, None, self.results
        
        # Make the other player's move
        move_result = self.player_2.make_player_move()
        
        # Check if this player is in checkmate or its a stalemate
        if move_result == None:
            if self.board.is_king_in_check(self.board.turn):
                self.results = game_results.black if self.board.turn == color.white else game_results.white
                self.play_sound("checkmate")
            else:
                self.results = game_results.stalemate
            self.play_sound("game-end")
            return True, None, self.results
        else:
            if get_move_capture(move):
                self.play_sound("capture")
            else:
                self.play_sound("move")
            self.game_data["positions"].append(self.board.to_scoreboard_array())

        # Check if the graphics player have a valid move to play
        if self.board.halfmove > 50:
            self.results = game_results.stalemate
            self.play_sound("game-end")
            return True, move_result, self.results

        # Check if the graphics player have a valid move to play
        board_copy = self.board.copy_board()
        graphics_move_result = self.player_1.make_player_move()
        
        if graphics_move_result == None: # If move is not possible
            if self.board.is_king_in_check(self.board.turn):
                self.results = game_results.black if self.board.turn == color.white else game_results.white
                self.play_sound("checkmate")
            else:
                self.results = game_results.stalemate
            self.play_sound("game-end")
            return True, move_result, self.results
        else:
            if get_move_capture(move_result):
                self.play_sound("capture")
            else:
                self.play_sound("move")
            self.board.restore_board(*board_copy)
        
        return True, move_result, None
