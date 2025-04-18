from unittest import result
from headers import *
from bit import *
from board import Board
from move import *

def perft_driver(board: Board, depth: int) -> int:
    """
    Recursively calculates the number of possible legal moves in a chess position 
    up to a given depth, commonly used for debugging and validating chess engines.
    """
    if depth == 0:
        return 1
    
    moves = board.generate_moves()
    count = 0
    for move in moves:
        copy = board.copy_board()
        if board.make_move(move, move_type.all_moves):
            count += perft_driver(board, depth - 1)
            board.restore_board(*copy)

    return count

def perft_test(starting_fen: str, depth: int) -> int:
    """
    Performs a perft (performance test) on a chess position to count the total number 
    of legal moves at a given depth. This is commonly used to validate the correctness 
    of a chess engine's move generation.
    """
    board = Board(starting_fen)
    if depth == 0:
        return 1
    
    moves = board.generate_moves()
    total = 0
    for move in moves:
        copy = board.copy_board()
        if board.make_move(move, move_type.all_moves):
            count = perft_driver(board, depth - 1)
            print(f"{str_move(move)}: {count}")
            board.restore_board(*copy)
            total += count

    return total

if __name__ == "__main__":
    result = perft_test("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 4)
    print(f"Total moves: {result}") # Expecting 4085603