def get_bit(bitboard: int, square: int) -> int:
    """Get the bit at the specified square."""
    return bitboard & (1 << square)

def set_bit(bitboard: int, square: int) -> int:
    """Set the bit at the specified square."""
    return bitboard | (1 << square)

def pop_bit(bitboard: int, square: int) -> int:
    """Clear the bit at the specified square."""
    return bitboard & ~(1 << square)

def get_ls1b_index(bitboard: int) -> int:
    """Get the index of the least significant bit (LSB) in the bitboard."""
    if bitboard == 0:
        return -1
    return ((bitboard & -bitboard) - 1).bit_count()

def print_bitboard(bitboard: int) -> None:
    """Print the bitboard in a human-readable format."""
    for rank in range(7, -1, -1):
        print(f"{rank + 1} ", end="")
        for file in range(8):
            square = rank * 8 + file
            print("⬜" if get_bit(bitboard, square) else "⬛", end="")
        print()
    print("   a b c d e f g h")


