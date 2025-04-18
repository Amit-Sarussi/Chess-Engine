import pygame

from bit import get_ls1b_index
from board import Board

from headers import *
from move import encode_move, get_move_source, get_move_target


class Graphics:
    def __init__(self, board: Board, controller) -> None:
        pygame.init()
        self.board = board
        self.controller = controller
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.last_squares = []
        self.hovered_square = 0
        self.holden_square = None
        self.holden_piece = None
        self.cursor_position = (0, 0)
        self.sprites_cache = self.load_sprites()  # Cache the sprites
        self.font = pygame.font.Font("assets/ChessSans.ttf", 24)
        self.loop()
        
    def load_sprites(self):
        """
        Loads and processes chess piece sprites for the game.
        """
        sprites = {}
        for i, piece_codename in enumerate(pieces_sprites):
            sprite = pygame.image.load(f"assets/pieces/{piece_codename}.png")  # Load the sprite
            sprite = pygame.transform.smoothscale(sprite, (WINDOW_SIZE // 8, WINDOW_SIZE // 8))  # Smoothly scale the sprite
            sprites[i] = sprite
        return sprites

    def loop(self):
        """
        Main event loop for the chess engine's graphical interface.
        This method handles user input events, updates the game state, and renders
        the graphical elements of the chessboard and pieces. It runs continuously
        until the user exits the application.
        Event Handling:
            - Tracks mouse motion to update the cursor position and determine the
              hovered square and cursor shape.
            - Handles mouse button presses and releases to interact with the game.
            - Detects the quit event to terminate the loop.
        Rendering:
            - Draws the chessboard squares, coordinates, pieces, and any piece
              currently being held by the user.
            - Updates the display after rendering.
        Cleanup:
            - Quits the pygame library when the loop ends.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    x, y = pygame.mouse.get_pos()
                    self.cursor_position = (x, y)
                    self.check_hover_square(x, y)
                    self.determine_cursor_shape()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_up()
                    
                if event.type == pygame.QUIT:
                    running = False
                
            self.draw_squares()
            self.draw_coordinates()
            self.draw_pieces()
            self.draw_holden_piece()
            
            # Flip the display
            pygame.display.flip()
        
        pygame.quit()
    
    def draw_squares(self):
        """
        Draws the chessboard squares on the screen.
        This method iterates through an 8x8 grid representing the chessboard.
        It alternates between light and dark tiles based on the row and column indices.
        """
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 0:
                    if (7 - row) * 8 + col in self.last_squares:
                        color = LIGHT_TILE_SELECTED
                    else:
                        color = LIGHT_TILE
                else:
                    if (7 - row) * 8 + col in self.last_squares:
                        color = DARK_TILE_SELECTED
                    else:
                        color = DARK_TILE
                
                pygame.draw.rect(self.screen, color, (col * (WINDOW_SIZE // 8), row * (WINDOW_SIZE // 8), WINDOW_SIZE // 8, WINDOW_SIZE // 8))
    
    def draw_coordinates(self):
        """
        Draws the chessboard coordinates (numbers and letters) on the screen.
        """
        for i in range(8):
            # Draw numbers (1-8) on the left side of the board
            number = self.font.render(str(8 - i), True, DARK_TILE if i % 2 == 0 else LIGHT_TILE)
            self.screen.blit(number, (5, i * (WINDOW_SIZE // 8) + 5))
            
            # Draw letters (a-h) on the bottom of the board
            letter = self.font.render(chr(ord('a') + i), True, LIGHT_TILE if i % 2 == 0 else DARK_TILE)
            self.screen.blit(letter, ((i + 1) * (WINDOW_SIZE // 8) - letter.get_width() - 5, WINDOW_SIZE - 30))
            
    def draw_pieces(self):
        """
        Draws the chess pieces on the board.
        This method iterates through the bitboards representing the positions of 
        each type of chess piece and draws the corresponding sprite on the screen 
        at the appropriate location. It uses cached sprites for efficiency.
        The method also checks if a piece is currently being held (dragged) by the 
        user and skips drawing it on the board, storing its type for later use.
        """
        for i, bitboard in enumerate(self.board.bitboards):
            sprite = self.sprites_cache[i]  # Use the cached sprite
            while bitboard:
                index = get_ls1b_index(bitboard)  # Calculate the index of the bit
                bitboard &= bitboard - 1  # Remove the least significant bit
                
                if self.holden_square is not None and index == self.holden_square:
                    self.holden_piece = i
                    continue
                
                col = index % 8
                row = 7 - (index // 8)
                self.screen.blit(sprite, (col * (WINDOW_SIZE // 8), row * (WINDOW_SIZE // 8)))  # Draw the sprite

    def check_hover_square(self, x, y):
        """
        Determines the chessboard square being hovered over based on the given 
        x and y pixel coordinates, and updates the `hovered_square` attribute.
        """
        col = x // (WINDOW_SIZE // 8)
        row = 7 - (y // (WINDOW_SIZE // 8))
        self.hovered_square = max(min(col + row * 8, 63), 0)
    
    def determine_cursor_shape(self):
        """
        Updates the cursor shape based on the hovered square on the chessboard.

        If the hovered square contains a piece belonging to the current player 
        (white), the cursor is set to a hand shape to indicate interactivity. 
        Otherwise, the cursor is set to the default arrow shape.
        """
        # Hand if hovered on its own piece
        if self.board.occupancies[color.white] & (1 << self.hovered_square):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def draw_holden_piece(self):
        """
        Draws the currently held chess piece sprite at the cursor's position.
        """
        if self.holden_piece != None:
            sprite = self.sprites_cache[self.holden_piece]  # Use the cached sprite
            x, y = self.cursor_position
            offset = (WINDOW_SIZE // 16)  # Half of the sprite size
            self.screen.blit(sprite, (x - offset, y - offset))  # Draw the sprite centered on the cursor
    
    def mouse_down(self):
        """
        Handles the mouse down event for the chessboard.
        """
        if self.board.occupancies[color.white] & (1 << self.hovered_square):
            self.holden_square = self.hovered_square
        self.last_squares = [self.holden_square]
    
    def mouse_up(self):
        """
        Handles the mouse button release event during a chess game.
        This method is responsible for processing the player's move when the mouse
        button is released. It determines the type of move (e.g., promotion, capture,
        double push, en passant, castling), encodes the move, and communicates it to
        the game controller. If the move is valid, it updates the game state and 
        handles the bot's response move if applicable.
        """
        self.last_squares = [self.holden_square]
        if self.holden_square is not None:
            from_square = self.holden_square
            to_square = self.hovered_square
            
            if from_square != to_square:
                # Get data about the move
                # Promotion
                promotion = 0 # Later to be implemented
                # Capture
                capture = self.board.occupancies[color.black] & (1 << to_square) != 0
                # Double push
                double_push = self.holden_piece == piece.P and (from_square - to_square) in (16, -16)
                # En passant
                enpassant = self.holden_piece == piece.P and (from_square - to_square) in (7, -7) and self.board.en_passant == to_square
                # Castling
                castling = (self.holden_piece == piece.K and (from_square - to_square) in (2, -2))
                
                # Encode the move
                move = encode_move(from_square, to_square, self.holden_piece, promotion, capture, double_push, enpassant, castling)
                status, bots_move, game_state = self.controller.make_move(move)
                if bots_move:
                    self.last_squares = [get_move_source(bots_move), get_move_target(bots_move)]
                    
            self.holden_square = None
            self.holden_piece = None