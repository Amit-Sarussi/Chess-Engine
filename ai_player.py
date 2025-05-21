import random
from board import Board
from player import Player
from headers import *
import numpy as np

class AIPlayer(Player):
    """
    SmartPlayer is a subclass of Player that represents a chess player 
    using a database to evaluate and make moves.
    """
    def __init__(self, board: Board, model, color: int = color.black) -> None:
        super().__init__(board, color)
        self.model = model
    
    def fen_to_tensor(self, fen: str) -> np.ndarray:
        """Convert a FEN-like string to a (8, 8, 17) tensor for CNN input."""
        values = list(map(int, fen[1:-1].split(",")))
        assert len(values) == 69, f"Expected 69 values (64 board + 4 castling + 1 ep), got {len(values)}"

        board_flat = values[:64]
        castling = values[64:68]
        ep_square = values[68]

        tensor = np.zeros((8, 8, 17), dtype=np.int8)

        # Piece planes (1–12)
        for i, val in enumerate(board_flat):
            if val == 0:
                continue
            plane = val - 1  # piece IDs are 1–12
            row, col = divmod(i, 8)
            tensor[row, col, plane] = 1

        # Castling planes (planes 12–15): broadcast across the whole 8x8 grid
        for i, right in enumerate(castling):
            tensor[:, :, 12 + i] = right

        # En passant plane (16)
        if ep_square != 0:
            row, col = divmod(ep_square, 8)
            tensor[row, col, 16] = 1

        return tensor

    def make_player_move(self) -> int | None:
        """
        Make a move using the AI model.
        This method generates all possible moves, evaluates them using the AI model,
        and selects the best move based on the evaluation scores.
        """
        all_moves = self.board.generate_moves()
        if not all_moves:
            return None

        fens = []
        moves_to_evaluate = []
        for move in all_moves:
            restore = self.board.copy_board()
            result = self.board.make_move(move)
            if result:
                fens.append(self.board.to_scoreboard_array())
                moves_to_evaluate.append(move)
                self.board.restore_board(*restore)  # Restore *after* appending
            else:
                # if a move is invalid, don't add it to list.
                pass

        if not fens:  # No valid moves
            return None

        tensors = np.array([self.fen_to_tensor(fen) for fen in fens])
        evaluations = self.model.predict(tensors, verbose=0).flatten()  # Get all evals at once

        moves_with_evaluations = list(zip(moves_to_evaluate, evaluations))
        moves_with_evaluations.sort(key=lambda x: x[1], reverse=True) # Sort by the evaluation

        for move, _ in moves_with_evaluations:
            status = self.board.make_move(move)
            if status:
                return move
        return None
