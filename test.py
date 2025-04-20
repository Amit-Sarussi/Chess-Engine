from LMDB import LMDBWrapper
from board import Board


db = LMDBWrapper("scoreboards")
print(item := db.get_random_item())

board = Board()
print(board.from_scoreboard_array(item[0]))

# ('[0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,0,0,0,0,0,0,0,0,0,12,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,-1]', (0.2187, 1))