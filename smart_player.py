import random
from board import Board
from player import Player
from headers import *

class SmartPlayer(Player):
    """
    SmartPlayer is a subclass of Player that represents a chess player 
    using a database to evaluate and make moves.
    """
    def __init__(self, board: Board, db, color: int = color.black) -> None:
        super().__init__(board, color)
        self.db = db

    def make_player_move(self) -> int | None:
        """
        Executes the best possible move for the player based on pre-evaluated scores
        from a database or a default score. Returns the chosen move or None if no
        valid moves are available.
        """
        all_moves = self.board.generate_moves()
        moves_with_evaluations = []
        
        # Sort them by evaluation
        for move in all_moves:
            # Get move's FEN:
            FEN = ""
            restore = self.board.copy_board()
            result = self.board.make_move(move)
            
            if result:
                FEN = self.board.to_scoreboard_array()
                self.board.restore_board(*restore)
            else:
                continue
            
            if (data := self.db.get(FEN)) is not None:
                moves_with_evaluations.append((move, data[0]))
            else:
                moves_with_evaluations.append((move, 0))
        
        moves_with_evaluations.sort(key=lambda x: x[1], reverse=True)
        while len(moves_with_evaluations) != 0:
            move = moves_with_evaluations[0][0]
            status = self.board.make_move(move)
            if status:
                return move
            else:
                moves_with_evaluations.remove(move)
                
        return None