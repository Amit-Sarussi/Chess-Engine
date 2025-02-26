from headers import *
from bit import *

def mask_pawn_attacks(color: int, square: int) -> int:
    """Calculate the attacks from a pawn at the given square."""
    attacks = 0 # Result attacks bitboard
    bitboard = 0 # Piece bitboard
    
    # Set piece on board
    bitboard = set_bit(bitboard, square)
    
    # White pawns
    if color == color.white:
        attacks |= (bitboard << 7) & NOT_H_FILE
        attacks |= (bitboard << 9) & NOT_A_FILE
    # Black pawns
    else:
        attacks |= (bitboard >> 7) & NOT_A_FILE
        attacks |= (bitboard >> 9) & NOT_H_FILE
    
    return attacks

def mask_knight_attacks(square: int) -> int:
    """Calculate the attacks from a knight at the given square."""
    attacks = 0 # Result attacks bitboard
    bitboard = 0 # Piece bitboard
    
    # Set piece on board
    bitboard = set_bit(bitboard, square)
    
    # Knight attacks
    attacks |= (bitboard << 17) & NOT_A_FILE
    attacks |= (bitboard << 15) & NOT_H_FILE
    attacks |= (bitboard << 10) & NOT_AB_FILE
    attacks |= (bitboard << 6) & NOT_HG_FILE
    attacks |= (bitboard >> 6) & NOT_AB_FILE
    attacks |= (bitboard >> 10) & NOT_HG_FILE
    attacks |= (bitboard >> 15) & NOT_A_FILE
    attacks |= (bitboard >> 17) & NOT_H_FILE
    
    return attacks

def mask_king_attacks(square: int) -> int:
    """Calculate the attacks from a king at the given square."""
    attacks = 0 # Result attacks bitboard
    bitboard = 0 # Piece bitboard
    
    # Set piece on board
    bitboard = set_bit(bitboard, square)
    
    # King attacks
    attacks |= (bitboard >> 8) # DOWN
    attacks |= (bitboard << 8) & 0xFFFFFFFFFFFFFFFF # UP
    attacks |= (bitboard >> 9) & NOT_H_FILE  # DOWN-LEFT
    attacks |= (bitboard << 9) & NOT_A_FILE  # UP-RIGHT
    attacks |= (bitboard >> 7) & NOT_A_FILE  # DOWN-RIGHT
    attacks |= (bitboard << 7) & NOT_H_FILE  # UP-LEFT
    attacks |= (bitboard >> 1) & NOT_H_FILE  # LEFT
    attacks |= (bitboard << 1) & NOT_A_FILE  # RIGHT
    
    return attacks

def init_leapers_attacks() -> tuple[list[list[int]], list[int], list[int]]:
    """Initialize the attacks bitboards for pawns, knights and kings."""
    pawn_attacks = [[0] * 64 for _ in range(2)] # [color][square] (2)(64)
    knight_attacks = [0 for _ in range(64)] # [square] (64)
    king_attacks = [0 for _ in range(64)] # [square] (64)
    for square in range(64):
        pawn_attacks[color.white][square] = mask_pawn_attacks(color.white, square)
        pawn_attacks[color.black][square] = mask_pawn_attacks(color.black, square)
        
        knight_attacks[square] = mask_knight_attacks(square)
        
        king_attacks[square] = mask_king_attacks(square)
    
    return pawn_attacks, knight_attacks, king_attacks

def mask_bishop_attacks(square: int) -> int:
    """Calculate the attacks from a bishop at the given square."""
    attacks = 0 # Result attacks bitboard
    
    tr = square // 8
    tf = square % 8
    
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dr, df in directions:
        r, f = tr + dr, tf + df
        while 1 <= r <= 6 and 1 <= f <= 6:
            attacks |= (1 << (r * 8 + f))
            r += dr
            f += df

    return attacks

def mask_rook_attacks(square: int) -> int:
    """Calculate the attacks from a rook at the given square."""
    attacks = 0 # Result attacks bitboard
    
    tr = square // 8
    tf = square % 8
    
    # Generate attacks on the rank
    for r in range(tr + 1, 7):
        attacks |= 1 << (r * 8 + tf)
    for r in range(tr - 1, 0, -1):
        attacks |= 1 << (r * 8 + tf)
    
    # Generate attacks on the file
    for f in range(tf + 1, 7):
        attacks |= 1 << (tr * 8 + f)
    for f in range(tf - 1, 0, -1):
        attacks |= 1 << (tr * 8 + f)

    return attacks

def generate_bishop_attacks_on_the_fly(square: int, blockers: int) -> int:
    """Calculate the attacks from a bishop at the given square, taking into account the given blockers."""
    attacks = 0 # Result attacks bitboard
    
    tr = square // 8
    tf = square % 8
    
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    for dr, df in directions:
        r, f = tr + dr, tf + df
        while 0 <= r <= 7 and 0 <= f <= 7:
            attacks |= (1 << (r * 8 + f))
            if get_bit(blockers, r * 8 + f):
                break
            r += dr
            f += df

    return attacks

def generate_rook_attacks_on_the_fly(square: int, blockers: int) -> int:
    """Calculate the attacks from a rook at the given square, taking into account the given blockers."""
    attacks = 0 # Result attacks bitboard
    
    tr = square // 8
    tf = square % 8
    
    # Generate attacks on the rank
    for r in range(tr + 1, 8):
        attacks |= 1 << (r * 8 + tf)
        if get_bit(blockers, r * 8 + tf):
            break
    for r in range(tr - 1, -1, -1):
        attacks |= 1 << (r * 8 + tf)
        if get_bit(blockers, r * 8 + tf):
            break
    
    # Generate attacks on the file
    for f in range(tf + 1, 8):
        attacks |= 1 << (tr * 8 + f)
        if get_bit(blockers, tr * 8 + f):
            break
    for f in range(tf - 1, -1, -1):
        attacks |= 1 << (tr * 8 + f)
        if get_bit(blockers, tr * 8 + f):
            break

    return attacks

def set_occupancy(index: int, bits_in_mask: int, attack_mask: int) -> int:
    """Return the occupancy bitboard for the given index and attack mask."""
    occupancy = 0
    
    for i in range(bits_in_mask):
        square = get_ls1b_index(attack_mask)
        
        attack_mask = pop_bit(attack_mask, square)
        
        if index & (1 << i):
           occupancy |= 1 << square
        
    return occupancy

import magics

bishop_masks, rook_masks, bishop_attacks, rook_attacks = magics.init_sliding_attacks()

def get_bishop_attacks(square: int, occupancy: int) -> int:
    """Get the bishop attacks for a given square and occupancy."""
    # Mask occupancy with bishop mask
    occupancy &= bishop_masks[square]
    # Multiply by magic number and mask to 64 bits
    occupancy = (occupancy * bishop_magic_numbers[square]) & 0xFFFFFFFFFFFFFFFF
    # Shift to get the attack index
    occupancy >>= 64 - bishop_relevant_bits[square]
    # Return the precomputed attacks
    return bishop_attacks[square][occupancy]

def get_rook_attacks(square: int, occupancy: int) -> int:
    """Get the rook attacks for a given square and occupancy."""
    # Mask occupancy with rook mask
    occupancy &= rook_masks[square]
    # Multiply by magic number and mask to 64 bits
    occupancy = (occupancy * rook_magic_numbers[square]) & 0xFFFFFFFFFFFFFFFF
    # Shift to get the attack index
    occupancy >>= 64 - rook_relevant_bits[square]
    # Return the precomputed attacks
    return rook_attacks[square][occupancy]

def get_queen_attacks(square: int, occupancy: int) -> int:
    """Get the queen attacks for a given square and occupancy."""
    return get_bishop_attacks(square, occupancy) | get_rook_attacks(square, occupancy)