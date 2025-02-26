from headers import *
from bit import *
from attacks import *
import random

def generate_magic_number_candidate():
    """Generate a random number to be used as a candidate for a magic number."""
    prime = 2147483647  # A good prime number
    return (random.getrandbits(64) * prime) & 0xFFFFFFFFFFFFFFFF

def find_magic_number(square: int, relevant_bits: int, piece_type: int) -> int:
    """Find the magic number for the given square, relevant bits and piece type."""
    # Initialize occupancies, attacks and used attacks tables
    occupancies = [0 for _ in range(4096)] # Init occupancies [square] (4096)
    attacks = [0 for _ in range(4096)] # Init attack tables [square] (4096)
    used_attacks = [0 for _ in range(4096)] # Init used attack tables [square] (4096)
    
    # Generate attack mask for a current piece
    attack_mask = mask_bishop_attacks(square) if piece_type == slide_piece.bishop else mask_rook_attacks(square)
    
    # Generate occupancies for a current piece
    occupancy_indicies = 1 << relevant_bits # Init occupancy indicies
    for index in range(occupancy_indicies):
        occupancies[index] = set_occupancy(index, relevant_bits, attack_mask) # Set occupancy for a current index
        
        # Generate attacks for a current index
        if piece_type == slide_piece.bishop:
            attacks[index] = generate_bishop_attacks_on_the_fly(square, occupancies[index])
        else:
            attacks[index] = generate_rook_attacks_on_the_fly(square, occupancies[index])
            
    # Test magic numbers
    max_random_count = 1000000000
    for _ in range(max_random_count):
        magic_number = generate_magic_number_candidate()
        
        # First filtering
        relevant_attack_bits = attack_mask & 0xFFFFFFFFFFFFFFFF # Ensure unsigned representation
        if relevant_attack_bits != 0: # Check if there are relevant bits
            if (relevant_attack_bits * magic_number).bit_count() < 6: # Check the relevant bits
                continue
        
        # Check for every possible occupancy index
        index, fail = 0, 0
        while not fail and index < occupancy_indicies:
            magic_index = ((occupancies[index] * magic_number) & 0xFFFFFFFFFFFFFFFF) >> (64 - relevant_bits)

            if used_attacks[magic_index] == 0:
                used_attacks[magic_index] = attacks[index]
            elif used_attacks[magic_index] != attacks[index]:
                fail = 1
            
            index += 1
        
        if not fail:
            return magic_number
    
    print("Magic number not found..")
    return 0

def init_magic_numbers() -> None:
    """Initialize the magic numbers for bishops and rooks."""
    print(f"------ BISHOP MAGIC NUMBERS ------")
    for square in range(64):
        print(find_magic_number(square, bishop_relevant_bits[square], slide_piece.bishop))
        
    print(f"------ ROOK MAGIC NUMBERS ------")
    for square in range(64):
        print(find_magic_number(square, rook_relevant_bits[square], slide_piece.rook))

def init_sliding_attacks() -> tuple[list[int], list[int], dict[int, dict[int, int]], dict[int, dict[int, int]]]:
    """Initialize the attacks, masks and magic numbers for the given sliding piece type."""
    bishop_masks = [0 for _ in range(64)]  # Initialize bishop masks
    rook_masks = [0 for _ in range(64)]  # Initialize rook masks
    bishop_attacks = [{} for _ in range(64)]  # Initialize bishop attacks
    rook_attacks = [{} for _ in range(64)]  # Initialize rook attacks
    
    for square in range(64):
        bishop_masks[square] = mask_bishop_attacks(square)  # Set bishop attack mask
        
        attack_mask = mask_bishop_attacks(square)  # Get bishop attack mask
        
        relevant_bits = attack_mask.bit_count()  # Count relevant bits
        occupancy_indicies = 1 << relevant_bits  # Calculate occupancy indices
        
        for index in range(occupancy_indicies):
            occupancy = set_occupancy(index, relevant_bits, attack_mask)  # Set occupancy
            magic_index = ((occupancy * bishop_magic_numbers[square]) & 0xFFFFFFFFFFFFFFFF) >> (64 - bishop_relevant_bits[square])  # Calculate magic index
            bishop_attacks[square][magic_index] = generate_bishop_attacks_on_the_fly(square, occupancy)  # Generate bishop attacks
    
    for square in range(64):
        rook_masks[square] = mask_rook_attacks(square)  # Set rook attack mask
        
        attack_mask = mask_rook_attacks(square)  # Get rook attack mask
        
        relevant_bits = attack_mask.bit_count()  # Count relevant bits
        occupancy_indicies = 1 << relevant_bits  # Calculate occupancy indices
        
        for index in range(occupancy_indicies):
            occupancy = set_occupancy(index, relevant_bits, attack_mask)  # Set occupancy
            magic_index = ((occupancy * rook_magic_numbers[square]) & 0xFFFFFFFFFFFFFFFF) >> (64 - rook_relevant_bits[square])  # Calculate magic index
            rook_attacks[square][magic_index] = generate_rook_attacks_on_the_fly(square, occupancy)  # Generate rook attacks
    
    return bishop_masks, rook_masks, bishop_attacks, rook_attacks  # Return initialized data
    
if __name__ == "__main__":
    init_magic_numbers()

