import numpy as np
from attacks import pop_bit
from bit import get_ls1b_index
from board import Board
from player import Player
from headers import *
import random

class piece_score(IntEnum):
    king = 200
    queen = 9
    rook = 5
    bishop = 3
    knight = 3
    pawn = 1

class HeuristicsPlayer(Player):
    def __init__(self, board: Board, color: int = color.white) -> None:
        super().__init__(board, color)

    def make_player_move(self):
        all_moves = self.board.generate_moves()
        
        move_evaluations = [(move, self.evaluate_move(move)) for move in all_moves] # Attaching an evaluation to each of the moves
        move_evaluations = [x for x in move_evaluations if x[1] is not None] # Removing illegal moves
        move_evaluations.sort(key=lambda x: x[1], reverse=True) # Sorting by evaluations

        if len(move_evaluations) == 0:
            return None
        else:
            self.board.make_move(move_evaluations[0][0], move_type.all_moves)
            return move_evaluations[0][0]
            
    def evaluate_move(self, move):
        before = self.board.copy_board()
        status = self.board.make_move(move, move_type.all_moves)
        evaluation = None
        if status:
            evaluation = self.evaluate_position()
        self.board.restore_board(*before)
        return evaluation
            
    def evaluate_position(self):
        piece_count = [self.board.bitboards[i].bit_count() for i in range(12)]
        material_score = piece_score.king * (piece_count[piece.K] - piece_count[piece.k]) + \
                         piece_score.queen * (piece_count[piece.Q] - piece_count[piece.q]) + \
                         piece_score.rook * (piece_count[piece.R] - piece_count[piece.r]) + \
                         piece_score.knight * (piece_count[piece.N] - piece_count[piece.n]) + \
                         piece_score.bishop * (piece_count[piece.B] - piece_count[piece.b]) + \
                         piece_score.pawn * (piece_count[piece.P] - piece_count[piece.p])
        
        who_to_move = 1 if self.color == color.white else -1
        return (material_score) * who_to_move