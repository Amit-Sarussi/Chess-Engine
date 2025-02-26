from board import Board
from headers import *

def convert_game_to_fens(game_data):
    starting_fen = game_data["start_fen"]
    board = Board(starting_fen)
    moves = game_data["moves"]
    fens = [starting_fen]
    for move in moves:
        board.make_move(move, move_type.all_moves)
        board_fen = board.to_fen()
        fens.append(board_fen)
    return fens