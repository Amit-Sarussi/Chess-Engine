from headers import *
from bit import *
from attacks import init_leapers_attacks, get_bishop_attacks, get_rook_attacks, get_queen_attacks
from magics import *
from move import *

class Board:
    def __init__(self, starting_fen: str = START_POSITION) -> None:
        self.pawn_attacks, self.knight_attacks, self.king_attacks = init_leapers_attacks()
        self.parse_fen(starting_fen)
    
    def print_board(self) -> None:
        """Prints the current state of the chess board, including piece positions and game status."""
        for rank in range(7, -1, -1):
            print(f"{rank + 1} ", end="")
            for file in range(8):
                square = rank * 8 + file
                piece = -1
                for i in range(12):
                    if get_bit(self.bitboards[i], square):
                        piece = i
                        break
                if piece == -1:
                    print(".", end=" ")
                else:
                    print(unicode_pieces[piece], end=" ")
            print()
        print("  a b c d e f g h\n")
        print(f"  Turn: {int_color[self.turn]}")
        print(f"  En passant: {square_to_coordinates[self.en_passant] if self.en_passant != -1 else 'no'}")
        
        castle_str = ""
        if self.castle & castle.wk:
            castle_str += "K"
        if self.castle & castle.wq:
            castle_str += "Q"
        if self.castle & castle.bk:
            castle_str += "k"
        if self.castle & castle.bq:
            castle_str += "q"
        
        if castle_str == "":
            castle_str = "-"
                
        print(f"  Castle: {castle_str}\n")
   
    def copy_board(self):
        bitboards_copy = self.bitboards.copy()
        occupancies_copy = self.occupancies.copy()
        turn_copy = self.turn  
        castle_copy = self.castle
        en_passant_copy = self.en_passant
        halfmove_copy = self.halfmove
        fullmove_copy = self.fullmove
        
        return (bitboards_copy, occupancies_copy, turn_copy, castle_copy, en_passant_copy, halfmove_copy, fullmove_copy)
    
    def restore_board(self, bitboards_copy, occupancies_copy, turn_copy, castle_copy, en_passant_copy, halfmove_copy, fullmove_copy):
        self.bitboards = bitboards_copy.copy()
        self.occupancies = occupancies_copy.copy()
        self.turn = turn_copy
        self.castle = castle_copy
        self.en_passant = en_passant_copy
        self.halfmove = halfmove_copy
        self.fullmove = fullmove_copy
    
    def parse_fen(self, FEN: str) -> None:
        """Parses a FEN string into the current board state. The FEN string should contain all information about the board state, including the piece positions, turn, en passant target, and castling rights."""
        # Reset board state
        self.bitboards = [0 for _ in range(12)]
        self.occupancies = [0 for _ in range(3)]
        self.en_passant = square.no_sq
        self.castle = 0
        
        # Split FEN string into components
        parts = FEN.split()
        board_part, turn_part, castle_part, en_passant_part, halfmove, fullmove = parts[:6]
        
        # Parse board position
        rank, file = 7, 0
        for char in board_part:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                piece_type = char_pieces[char]
                square_index = rank * 8 + file
                self.bitboards[piece_type] = set_bit(self.bitboards[piece_type], square_index)
                file += 1
        
        # Parse turn
        self.turn = color.white if turn_part == 'w' else color.black
        
        # Parse castling rights
        if castle_part != '-':
            for char in castle_part:
                if char == 'K': self.castle |= castle.wk
                elif char == 'Q': self.castle |= castle.wq
                elif char == 'k': self.castle |= castle.bk
                elif char == 'q': self.castle |= castle.bq
        
        # Parse en passant square
        if en_passant_part != '-':
            file, rank = ord(en_passant_part[0]) - ord('a'), int(en_passant_part[1]) - 1
            self.en_passant = rank * 8 + file
        
        # Update occupancies
        for piece in range(12):
            self.occupancies[color.white] |= self.bitboards[piece] if piece < 6 else 0
            self.occupancies[color.black] |= self.bitboards[piece] if piece >= 6 else 0
        self.occupancies[color.both] = self.occupancies[color.white] | self.occupancies[color.black]
        
        # Update clocks
        self.halfmove = int(halfmove)
        self.fullmove = int(fullmove)
     
    @staticmethod
    def validate_fen(fen: str) -> bool:
        """Validates a FEN string."""
        parts = fen.split()
        if len(parts) != 6:
            return False

        board_part, turn_part, castle_part, en_passant_part, halfmove_part, fullmove_part = parts

        # Validate board part
        ranks = board_part.split('/')
        if len(ranks) != 8:
            return False
        for rank in ranks:
            file_count = 0
            for char in rank:
                if char.isdigit():
                    file_count += int(char)
                elif char in 'PNBRQKpnbrqk':
                    file_count += 1
                else:
                    return False
            if file_count != 8:
                return False

        # Validate turn part
        if turn_part not in ('w', 'b'):
            return False

        # Validate castle part
        if castle_part != '-':
            for char in castle_part:
                if char not in 'KQkq':
                    return False

        # Validate en passant part
        if en_passant_part != '-':
            if len(en_passant_part) != 2:
                return False
            file, rank = en_passant_part
            if file not in 'abcdefgh' or rank not in '123456':
                return False

        # Validate halfmove part
        if not halfmove_part.isdigit():
            return False
        if int(halfmove_part) < 0:
            return False

        # Validate fullmove part
        if not fullmove_part.isdigit():
            return False
        if int(fullmove_part) < 1:
            return False

        return True

    def to_scoreboard_array(self) -> str:
        array = []
        for rank in range(8):
            for file in range(8):
                # Get the piece at the square
                square = rank * 8 + file
                for piece in range(12):
                    if get_bit(self.bitboards[piece], square):
                        array.append(piece + 1) # 0 is Empty
                        break
                else:
                    array.append(0)
        
        # Castling
        array.append(1 if castle.wk & self.castle else 0)
        array.append(1 if castle.wq & self.castle else 0)
        array.append(1 if castle.bk & self.castle else 0)
        array.append(1 if castle.bq & self.castle else 0)
        
        # En passant
        array.append(self.en_passant)

        return "[" + ",".join(map(str, array)) + "]"
    
    def from_scoreboard_array(self, scoreboard_str: str) -> str:
        import re

        # Parse the array string into integers
        array = list(map(int, re.findall(r'\d+', scoreboard_str)))
        assert len(array) == 64 + 4 + 1, "Invalid scoreboard array length"

        piece_map = {
            1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K',
            7: 'p', 8: 'n', 9: 'b', 10: 'r', 11: 'q', 12: 'k'
        }

        # Reconstruct board part of FEN
        fen_parts = []
        for rank in range(8):
            empty = 0
            row = ''
            for file in range(8):
                val = array[rank * 8 + file]
                if val == 0:
                    empty += 1
                else:
                    if empty > 0:
                        row += str(empty)
                        empty = 0
                    row += piece_map[val]
            if empty > 0:
                row += str(empty)
            fen_parts.append(row)
        board_fen = "/".join(fen_parts)

        # Castling
        wk, wq, bk, bq = array[64:68]
        castling_fen = (
            ('K' if wk else '') +
            ('Q' if wq else '') +
            ('k' if bk else '') +
            ('q' if bq else '')
        ) or '-'

        # En passant
        ep_square = array[68]
        if ep_square == 0:
            ep_fen = '-'
        else:
            file = ep_square % 8
            rank = ep_square // 8
            ep_fen = chr(ord('a') + file) + str(8 - rank)

        # Assume it's always white's turn and halfmove/fullmove are 0
        return f"{board_fen} w {castling_fen} {ep_fen} 0 1"
      
    def is_square_attacked(self, square: int, side: int) -> bool:
        """Determine if a given square is attacked by any piece of the specified side."""

        # Attacked by queens
        if side == color.white and get_queen_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.Q]: return True
        if side == color.black and get_queen_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.q]: return True
        
        # Attacked by bishops
        if side == color.white and get_bishop_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.B]: return True
        if side == color.black and get_bishop_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.b]: return True
        
        # Attacked by rooks
        if side == color.white and get_rook_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.R]: return True
        if side == color.black and get_rook_attacks(square, self.occupancies[color.both]) & self.bitboards[piece.r]: return True
        
        # Attacked by knights
        if side == color.white and self.knight_attacks[square] & self.bitboards[piece.N]: return True
        if side == color.black and self.knight_attacks[square] & self.bitboards[piece.n]: return True
        
        # Attacked by kings
        if side == color.white and self.king_attacks[square] & self.bitboards[piece.K]: return True
        if side == color.black and self.king_attacks[square] & self.bitboards[piece.k]: return True
        
        # Attacked by pawns
        if side == color.white and self.pawn_attacks[color.black][square] & self.bitboards[piece.P]: return True
        if side == color.black and self.pawn_attacks[color.white][square] & self.bitboards[piece.p]: return True
        
        return False
    
    def print_attacked_squares(self, color: int):
        """Print all squares attacked by the current player."""
        bb = 0
        for square in range(64):
            if self.is_square_attacked(square, color):
                bb = set_bit(bb, square)
        
        print_bitboard(bb)

    def generate_moves(self) -> list[int]:
        """Generate all moves for the current player."""
        moves = []
        # Loop over all bitboards
        for pc in range(12):
            bitboard = self.bitboards[pc]
            
            # Generate white pawns and white king castling moves
            if self.turn == color.white:
                if pc == piece.P:
                    # Look over white pawns within white pawn bitboard
                    while bitboard:
                        source_square = get_ls1b_index(bitboard)
                        target_square = source_square + 8
                        
                        # Quiet move
                        if not target_square < 0 and not get_bit(self.occupancies[color.both], target_square):
                            # Pawn promotion
                            if target_square // 8 == 7:
                                moves.append(encode_move(source_square, target_square, pc, piece.Q, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.R, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.B, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.N, 0, 0, 0, 0))
                            else:
                                # One square move
                                moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))
                                # Two square move
                                if source_square // 8 == 1 and not get_bit(self.occupancies[color.both], target_square + 8):
                                    moves.append(encode_move(source_square, target_square + 8, pc, 0, 0, 1, 0, 0))
                        
                        # Pawn attacks
                        attacks = self.pawn_attacks[self.turn][source_square] & self.occupancies[color.black]
                        while attacks:
                            target_square = get_ls1b_index(attacks)
                            
                            # Pawn promotion
                            if target_square // 8 == 7:
                                moves.append(encode_move(source_square, target_square, pc, piece.Q, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.R, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.B, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.N, 1, 0, 0, 0))
                            else:
                                moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0))                                
                                
                            attacks = pop_bit(attacks, target_square)
                        
                        # En passant
                        if self.en_passant != square.no_sq:
                            # Check if the current pawn can capture the en passant square
                            enpassant_attacks = self.pawn_attacks[self.turn][source_square] & (1 << self.en_passant)
                            
                            if enpassant_attacks:
                                moves.append(encode_move(source_square, self.en_passant, pc, 0, 1, 0, 1, 0))
                        
                        bitboard = pop_bit(bitboard, source_square)
                        
                # Generate white king castling moves
                elif pc == piece.K:
                    if self.castle & castle.wk:
                        # Make sure that square between king and rook are empty
                        if not get_bit(self.occupancies[color.both], square.f1) and not get_bit(self.occupancies[color.both], square.g1):
                            # Make sure king and the f1 squares are not attacked
                            if not self.is_square_attacked(square.e1, color.black) and not self.is_square_attacked(square.f1, color.black):
                                moves.append(encode_move(square.e1, square.g1, pc, 0, 0, 0, 0, 1))
                    if self.castle & castle.wq:
                        # Make sure that square between king and rook are empty
                        if not get_bit(self.occupancies[color.both], square.b1) and not get_bit(self.occupancies[color.both], square.c1) and not get_bit(self.occupancies[color.both], square.d1):
                            # Make sure king and the d1, c1 squares are not attacked
                            if not self.is_square_attacked(square.e1, color.black) and not self.is_square_attacked(square.d1, color.black):
                                moves.append(encode_move(square.e1, square.c1, pc, 0, 0, 0, 0, 1))
                            
            # Generate black pawns and black king castling moves
            else:
                if pc == piece.p:
                    # Look over black pawns within black pawn bitboard
                    while bitboard:
                        source_square = get_ls1b_index(bitboard)
                        target_square = source_square - 8
                        
                        # Quiet move
                        if not target_square < 0 and not get_bit(self.occupancies[color.both], target_square):
                            # Pawn promotion
                            if target_square // 8 == 0:
                                moves.append(encode_move(source_square, target_square, pc, piece.q, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.r, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.b, 0, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.n, 0, 0, 0, 0))
                            else:
                                # One square move
                                moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))
                                # Two square move
                                if source_square // 8 == 6 and not get_bit(self.occupancies[color.both], target_square - 8):
                                    moves.append(encode_move(source_square, target_square - 8, pc, 0, 0, 1, 0, 0))

                        # Pawn attacks
                        attacks = self.pawn_attacks[self.turn][source_square] & self.occupancies[color.white]
                        while attacks:
                            target_square = get_ls1b_index(attacks)
                            
                            # Pawn promotion
                            if target_square // 8 == 0:
                                moves.append(encode_move(source_square, target_square, pc, piece.q, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.r, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.b, 1, 0, 0, 0))
                                moves.append(encode_move(source_square, target_square, pc, piece.n, 1, 0, 0, 0))
                            else:
                                moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0))                                
                                
                                
                            attacks = pop_bit(attacks, target_square)
                        
                        # En passant
                        if self.en_passant != square.no_sq:
                            # Check if the current pawn can capture the en passant square
                            enpassant_attacks = self.pawn_attacks[self.turn][source_square] & (1 << self.en_passant)
                            
                            if enpassant_attacks:
                                moves.append(encode_move(source_square, self.en_passant, pc, 0, 1, 0, 1, 0))
                                
                        bitboard = pop_bit(bitboard, source_square)
                        
                # Generate black king castling moves
                elif pc == piece.k:
                    if self.castle & castle.bk:
                        # Make sure that square between king and rook are empty
                        if not get_bit(self.occupancies[color.both], square.f8) and not get_bit(self.occupancies[color.both], square.g8):
                            # Make sure king and the f1 squares are not attacked
                            if not self.is_square_attacked(square.e8, color.white) and not self.is_square_attacked(square.f8, color.white):
                                moves.append(encode_move(square.e8, square.g8, pc, 0, 0, 0, 0, 1))
                    if self.castle & castle.bq:
                        # Make sure that square between king and rook are empty
                        if not get_bit(self.occupancies[color.both], square.b8) and not get_bit(self.occupancies[color.both], square.c8) and not get_bit(self.occupancies[color.both], square.d8):
                            # Make sure king and the d1, c1 squares are not attacked
                            if not self.is_square_attacked(square.e8, color.white) and not self.is_square_attacked(square.d8, color.white):
                                moves.append(encode_move(square.e8, square.c8, pc, 0, 0, 0, 0, 1))
            
            # Generate knight moves
            if (self.turn == color.white and pc == piece.N) or (self.turn == color.black and pc == piece.n):
                while bitboard:
                    source_square = get_ls1b_index(bitboard)
                    attacks = self.knight_attacks[source_square] & ~self.occupancies[self.turn]
                    while attacks:
                        target_square = get_ls1b_index(attacks)
                        
                        # Quiet move
                        if not get_bit(self.occupancies[color.both], target_square):
                            moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))                        # Attack
                        else:
                            moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0))                           
                        attacks = pop_bit(attacks, target_square)
                    bitboard = pop_bit(bitboard, source_square)
            
            # Generate bishop moves
            if (self.turn == color.white and pc == piece.B) or (self.turn == color.black and pc == piece.b):
                while bitboard:
                    source_square = get_ls1b_index(bitboard)
                    attacks = get_bishop_attacks(source_square, self.occupancies[color.both]) & ~self.occupancies[self.turn]
                    while attacks:
                        target_square = get_ls1b_index(attacks)
                        
                        # Quiet move
                        if not get_bit(self.occupancies[color.both], target_square):
                            moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))  
                        # Attack
                        else:
                            moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0)) 
                        
                        attacks = pop_bit(attacks, target_square)
                    bitboard = pop_bit(bitboard, source_square)
            
            # Generate rook moves
            if (self.turn == color.white and pc == piece.R) or (self.turn == color.black and pc == piece.r):
                while bitboard:
                    source_square = get_ls1b_index(bitboard)
                    attacks = get_rook_attacks(source_square, self.occupancies[color.both]) & ~self.occupancies[self.turn]
                    while attacks:
                        target_square = get_ls1b_index(attacks)
                        
                        # Quiet move
                        if not get_bit(self.occupancies[color.both], target_square):
                            moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))  
                        # Attack
                        else:
                            moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0)) 
                        
                        attacks = pop_bit(attacks, target_square)
                    bitboard = pop_bit(bitboard, source_square)
                    
            # Generate queen moves
            if (self.turn == color.white and pc == piece.Q) or (self.turn == color.black and pc == piece.q):
                while bitboard:
                    source_square = get_ls1b_index(bitboard)
                    attacks = get_queen_attacks(source_square, self.occupancies[color.both]) & ~self.occupancies[self.turn]
                    while attacks:
                        target_square = get_ls1b_index(attacks)
                        
                        # Quiet move
                        if not get_bit(self.occupancies[color.both], target_square):
                            moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))  
                        # Attack
                        else:
                            moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0)) 
                        
                        attacks = pop_bit(attacks, target_square)
                    bitboard = pop_bit(bitboard, source_square)
            
            # Generate king moves
            if (self.turn == color.white and pc == piece.K) or (self.turn == color.black and pc == piece.k):
                while bitboard:
                    source_square = get_ls1b_index(bitboard)
                    attacks = self.king_attacks[source_square] & ~self.occupancies[self.turn]
                    
                    while attacks:
                        target_square = get_ls1b_index(attacks)
                        
                        # Quiet move
                        if not get_bit(self.occupancies[color.both], target_square):
                            moves.append(encode_move(source_square, target_square, pc, 0, 0, 0, 0, 0))  
                                                        
                        # Attack
                        else:
                            moves.append(encode_move(source_square, target_square, pc, 0, 1, 0, 0, 0)) 
                        
                        attacks = pop_bit(attacks, target_square)
                    bitboard = pop_bit(bitboard, source_square)
        
        return moves
                
    def make_move(self, move: int, move_flag: int):
        """Make a move on the board."""
        # Quiet move
        if move_flag == move_type.all_moves:
            # Preserve board state
            state = self.copy_board()
            
            # Parse move
            source_square = get_move_source(move)
            target_square = get_move_target(move)
            m_piece = get_move_piece(move)
            promoted = get_move_promoted(move)
            capture = get_move_capture(move)
            double_push = get_move_double_push(move)
            enpassant = get_move_enpassant(move)
            castling = get_move_castling(move)
            
            # Move piece
            self.bitboards[m_piece] = pop_bit(self.bitboards[m_piece], source_square)
            self.bitboards[m_piece] = set_bit(self.bitboards[m_piece], target_square)
            
            # Handle capture moves
            if capture:
                # Loop over bitboards opposite to current turn
                opposite_range = range(6) if self.turn == color.black else range(6, 12)
                for pce in opposite_range:
                    if get_bit(self.bitboards[pce], target_square):
                        self.bitboards[pce] = pop_bit(self.bitboards[pce], target_square)
                        break
            
            # Handle promotion moves
            if promoted:
                self.bitboards[m_piece] = pop_bit(self.bitboards[m_piece], target_square)
                self.bitboards[promoted] = set_bit(self.bitboards[promoted], target_square)
            
            # Handle en passant captures
            if enpassant:
                if self.turn == color.white:
                    self.bitboards[piece.p] = pop_bit(self.bitboards[piece.p], target_square - 8)
                else:
                    self.bitboards[piece.P] = pop_bit(self.bitboards[piece.P], target_square + 8)

            # Reset en passant square
            self.en_passant = square.no_sq
            
            # Handle double push
            if double_push:
                if self.turn == color.white:
                    self.en_passant = target_square - 8
                else:
                    self.en_passant = target_square + 8
            
            # Handle castling
            if castling:
                match target_square:
                    case square.g1:
                        self.bitboards[piece.R] = pop_bit(self.bitboards[piece.R], square.h1)
                        self.bitboards[piece.R] = set_bit(self.bitboards[piece.R], square.f1)
                    case square.c1:
                        self.bitboards[piece.R] = pop_bit(self.bitboards[piece.R], square.a1)
                        self.bitboards[piece.R] = set_bit(self.bitboards[piece.R], square.d1)
                    case square.g8:
                        self.bitboards[piece.r] = pop_bit(self.bitboards[piece.r], square.h8)
                        self.bitboards[piece.r] = set_bit(self.bitboards[piece.r], square.f8)
                    case square.c8:
                        self.bitboards[piece.r] = pop_bit(self.bitboards[piece.r], square.a8)
                        self.bitboards[piece.r] = set_bit(self.bitboards[piece.r], square.d8)

            # Update castling rights
            self.castle &= castling_rights[source_square]
            self.castle &= castling_rights[target_square]
            
            # Update occupancies
            self.occupancies[color.white] = self.bitboards[piece.P] | self.bitboards[piece.N] | self.bitboards[piece.B] | self.bitboards[piece.Q] | self.bitboards[piece.K] | self.bitboards[piece.R]
            self.occupancies[color.black] = self.bitboards[piece.p] | self.bitboards[piece.n] | self.bitboards[piece.b] | self.bitboards[piece.q] | self.bitboards[piece.k] | self.bitboards[piece.r]
            self.occupancies[color.both] = self.occupancies[color.white] | self.occupancies[color.black]
            
           
            # Update halfmove clock
            self.halfmove += 1
            if capture or m_piece == piece.p or m_piece == piece.P:
                self.halfmove = 0
                
            # Update fullmove clock
            if self.turn == color.black:
                self.fullmove += 1
            
            # Switch turn
            self.turn ^= 1
            
            # Make sure that king is not in check
            king_square = get_ls1b_index(self.bitboards[piece.k] if self.turn == color.white else self.bitboards[piece.K])
            if self.is_square_attacked(king_square, self.turn):
                # Move is illegal, take it back.
                self.restore_board(*state)
                return 0
                
            else:
                return 1
            
        # Capture move
        else:
            if get_move_capture(move):
                self.make_move(move, move_type.all_moves)
            else:
                # Dont make the move
                return 0
            
    def is_king_in_check(self, king_color):
        # get the king square
        king_square = get_ls1b_index(self.bitboards[piece.K if king_color == color.white else piece.k])
        
        other_color = color.black if king_color == color.white else color.white
        return self.is_square_attacked(king_square, other_color)
        

