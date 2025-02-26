"""
Move encoding:

The move is encoded in 24 bits. 
The first 6 bits store the source square,
the next 6 bits store the target square, 
the next 4 bits store the piece, 
the next 4 bits store the promoted piece,
and the next 3 bits store the flags. The flags are as follows:
          
0000  0000  0000  0000  0011  1111    source square      0x3f
0000  0000  0000  1111  1100  0000    target square      0xfc0
0000  0000  1111  0000  0000  0000    piece              0xf000
0000  1111  0000  0000  0000  0000    promoted piece     0xf000
0001  0000  0000  0000  0000  0000    capture flag       0x100000
0010  0000  0000  0000  0000  0000    double push flag   0x200000
0100  0000  0000  0000  0000  0000    enpassant flag     0x400000
1000  0000  0000  0000  0000  0000    castling flag      0x800000
"""

from headers import *


def encode_move(source: int, target: int, piece: int, promoted: int, capture: int, double_push: int, enpassant: int, castling: int) -> int:
    """Encode a chess move into a 24-bit integer by the defined format."""
    return source | (target << 6) | (piece << 12) | (promoted << 16) | (capture << 20) | (double_push << 21) | (enpassant << 22) | (castling << 23)

def print_move(move):
    print(str_move(move))

def str_move(move):
    move_str = f"{square_to_coordinates[get_move_source(move)]}{square_to_coordinates[get_move_target(move)]}"
    if get_move_promoted(move):
        move_str += f"{ascii_pieces[get_move_promoted(move)]}"
    return move_str
    
def print_moves(moves: list) -> None:
    """Print the moves in a human-readable table format."""
    print("  {:<8} {:<6} {:<8} {:<12} {:<10} {:<9}".format(
        "Move", "Piece", "Capture", "Double Push", "En Passant", "Castling"
    ))
    print()
    for i, move in enumerate(moves):
        move_str = f"{square_to_coordinates[get_move_source(move)]}{square_to_coordinates[get_move_target(move)]}"
        if get_move_promoted(move):
            move_str += ascii_pieces[get_move_promoted(move)].lower()
        print("  {:<8} {:<6} {:<8} {:<12} {:<10} {:<9}".format(
            move_str,
            ascii_pieces[get_move_piece(move)],
            get_move_capture(move),
            get_move_double_push(move),
            get_move_enpassant(move),
            get_move_castling(move)
        ))
    print(f"\n  Total moves: {i + 1}")
    
def get_move_source(move: int) -> int:
    """Get the source square from the move."""
    return move & 0x3f

def get_move_target(move: int) -> int:
    """Get the target square from the move."""
    return (move >> 6) & 0x3f

def get_move_piece(move: int) -> int:
    """Get the piece from the move."""
    return (move >> 12) & 0xf

def get_move_promoted(move: int) -> int:
    """Get the promoted piece from the move."""
    return (move >> 16) & 0xf

def get_move_capture(move: int) -> int:
    """Check if the move is a capture."""
    return (move >> 20) & 0x1

def get_move_double_push(move: int) -> int:
    """Check if the move is a double pawn push."""
    return (move >> 21) & 0x1

def get_move_enpassant(move: int) -> int:
    """Check if the move is an enpassant."""
    return (move >> 22) & 0x1

def get_move_castling(move: int) -> int:
    """Check if the move is a castling."""
    return (move >> 23) & 0x1
