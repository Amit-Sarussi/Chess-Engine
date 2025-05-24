from enum import IntEnum
from typing import Final


class square(IntEnum):
    a1, b1, c1, d1, e1, f1, g1, h1 = range(8)
    a2, b2, c2, d2, e2, f2, g2, h2 = range(8, 16)
    a3, b3, c3, d3, e3, f3, g3, h3 = range(16, 24)
    a4, b4, c4, d4, e4, f4, g4, h4 = range(24, 32)
    a5, b5, c5, d5, e5, f5, g5, h5 = range(32, 40)
    a6, b6, c6, d6, e6, f6, g6, h6 = range(40, 48)
    a7, b7, c7, d7, e7, f7, g7, h7 = range(48, 56)
    a8, b8, c8, d8, e8, f8, g8, h8 = range(56, 64)
    no_sq = -1

square_to_coordinates: Final = [f"{chr(97 + (i % 8))}{i // 8 + 1}" for i in range(64)]

class color(IntEnum):
    white = 0
    black = 1
    both = 2

int_color: Final = ["white", "black", "both"]

class piece(IntEnum):
    P,N,B,R,Q,K,p,n,b,r,q,k = range(12)

ascii_pieces: Final = "PNBRQKpnbrqk"
pieces_sprites: Final = ["wp", "wn", "wb", "wr", "wq", "wk", "bp", "bn", "bb", "br", "bq", "bk"]
unicode_pieces: Final = "♙♘♗♖♕♔♟♞♝♜♛♚"
char_pieces: Final = {
    'P': piece.P,
    'N': piece.N,
    'B': piece.B,
    'R': piece.R,
    'Q': piece.Q,
    'K': piece.K,
    'p': piece.p,
    'n': piece.n,
    'b': piece.b,
    'r': piece.r,
    'q': piece.q,
    'k': piece.k
}

class slide_piece(IntEnum):
    bishop = 0
    rook = 1


class player_type(IntEnum):
    random = 0
    heuristics = 1
    graphics = 4
    smart = 5
    ai = 6

class game_results(IntEnum):
    white = 0
    black = 1
    stalemate = 2

games_dir = "games"
scoreboard_dir = "scoreboards"


# Selection bitboards
NOT_A_FILE: Final = 18374403900871474942
NOT_H_FILE: Final = 9187201950435737471
NOT_HG_FILE: Final = 4557430888798830399
NOT_AB_FILE: Final = 18229723555195321596

# FEN debug positions
EMPTY_BOARD: Final = "8/8/8/8/8/8/8/8 w - - "
START_POSITION: Final = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 "
TRICKY_POSITION: Final = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1 "
KILLER_POSITION: Final = "rnbqkb1r/pp1p1pPp/8/2p1pP2/1P1P4/3P3P/P1P1P3/RNBQKBNR w KQkq e6 0 1"
CMK_POSITION: Final = "r2q1rk1/ppp2ppp/2n1bn2/2b1p3/3pP3/3P1NPP/PPP1NPB1/R1BQ1RK1 b - - 0 9 "
class castle(IntEnum):
    """
    bin   dec  
    0001  1     white king can castle to the king side  
    0010  2     white king can castle to the queen side  
    0100  4     black king can castle to the king side  
    1000  8     black king can castle to the queen side  

    examples  
    1111        both sides an castle both directions  
    1001        black king  => queen side  
                white king  => king side  
    """
    wk = 1
    wq = 2
    bk = 4
    bq = 8
    all = 15


#                                castling   move    in      in
#                                   right   update  binary  decimal

#    king & rooks didn’t move:       1111 & 1111  = 1111    15

#            white king moved:       1111 & 1100  = 1100    12
#     white king’s rook moved:       1111 & 1110  = 1110    14
#    white queen’s rook moved:       1111 & 1101  = 1101    13

#            black king moved:       1111 & 0011  = 1011    3
#     black king’s rook moved:       1111 & 1011  = 1011    11
#    black queen’s rook moved:       1111 & 0111  = 0111    7

# Castling rights lookup table for each square
castling_rights: Final = [
   13, 15, 15, 15, 12, 15, 15, 14,
   15, 15, 15, 15, 15, 15, 15, 15,
   15, 15, 15, 15, 15, 15, 15, 15,
   15, 15, 15, 15, 15, 15, 15, 15,
   15, 15, 15, 15, 15, 15, 15, 15,
   15, 15, 15, 15, 15, 15, 15, 15,
   15, 15, 15, 15, 15, 15, 15, 15,
    7, 15, 15, 15,  3, 15, 15, 11
]

# Bishop relevant occupancy bit count for every square on board
bishop_relevant_bits: Final = [
    6, 5, 5, 5, 5, 5, 5, 6, 
    5, 5, 5, 5, 5, 5, 5, 5, 
    5, 5, 7, 7, 7, 7, 5, 5, 
    5, 5, 7, 9, 9, 7, 5, 5, 
    5, 5, 7, 9, 9, 7, 5, 5, 
    5, 5, 7, 7, 7, 7, 5, 5, 
    5, 5, 5, 5, 5, 5, 5, 5,
    6, 5, 5, 5, 5, 5, 5, 6,
]

# Rook relevant occupancy bit count for every square on board
rook_relevant_bits: Final = [
    12, 11, 11, 11, 11, 11, 11, 12, 
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    11, 10, 10, 10, 10, 10, 10, 11,
    12, 11, 11, 11, 11, 11, 11, 12,
]

bishop_magic_numbers: Final = [
    9368648609924554880, 9009475591934976,     4504776450605056,
    1130334595844096,    1725202480235520,     288516396277699584,
    613618303369805920,  10168455467108368,    9046920051966080,
    36031066926022914,   1152925941509587232,  9301886096196101,
    290536121828773904,  5260205533369993472,  7512287909098426400,
    153141218749450240,  9241386469758076456,  5352528174448640064,
    2310346668982272096, 1154049638051909890,  282645627930625,
    2306405976892514304, 11534281888680707074, 72339630111982113,
    8149474640617539202, 2459884588819024896,  11675583734899409218,
    1196543596102144,    5774635144585216,     145242600416216065,
    2522607328671633440, 145278609400071184,   5101802674455216,
    650979603259904,     9511646410653040801,  1153493285013424640,
    18016048314974752,   4688397299729694976,  9226754220791842050,
    4611969694574863363, 145532532652773378,   5265289125480634376,
    288239448330604544,  2395019802642432,     14555704381721968898,
    2324459974457168384, 23652833739932677,    282583111844497,
    4629880776036450560, 5188716322066279440,  146367151686549765,
    1153170821083299856, 2315697107408912522,  2342448293961403408,
    2309255902098161920, 469501395595331584,   4615626809856761874,
    576601773662552642,  621501155230386208,   13835058055890469376,
    3748138521932726784, 9223517207018883457,  9237736128969216257,
    1127068154855556,
]

rook_magic_numbers: Final = [
    612498416294952992,  2377936612260610304,  36037730568766080,
    72075188908654856,   144119655536003584,   5836666216720237568,
    9403535813175676288, 1765412295174865024,  3476919663777054752,
    288300746238222339,  9288811671472386,     146648600474026240,
    3799946587537536,    704237264700928,      10133167915730964,
    2305983769267405952, 9223634270415749248,  10344480540467205,
    9376496898355021824, 2323998695235782656,  9241527722809755650,
    189159985010188292,  2310421375767019786,  4647717014536733827,
    5585659813035147264, 1442911135872321664,  140814801969667,
    1188959108457300100, 288815318485696640,   758869733499076736,
    234750139167147013,  2305924931420225604,  9403727128727390345,
    9223970239903959360, 309094713112139074,   38290492990967808,
    3461016597114651648, 181289678366835712,   4927518981226496513,
    1155212901905072225, 36099167912755202,    9024792514543648,
    4611826894462124048, 291045264466247688,   83880127713378308,
    1688867174481936,    563516973121544,      9227888831703941123,
    703691741225216,     45203259517829248,    693563138976596032,
    4038638777286134272, 865817582546978176,   13835621555058516608,
    11541041685463296,   288511853443695360,   283749161902275,
    176489098445378,     2306124759338845321,  720584805193941061,
    4977040710267061250, 10097633331715778562, 325666550235288577,
    1100057149646,
]


LIGHT_TILE: Final = (240, 217, 181)
LIGHT_TILE_SELECTED: Final = (207, 209, 128)
DARK_TILE: Final = (181, 136, 99)
DARK_TILE_SELECTED: Final = (170, 162, 80)
WINDOW_SIZE: Final = 1000
