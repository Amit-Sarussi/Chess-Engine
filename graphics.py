import ctypes
import os
import sys
import pygame

from bit import get_ls1b_index

from game import Game
from headers import *
from move import encode_move, get_move_source, get_move_target


class Graphics:
    def __init__(self, game: Game, controller) -> None:
        pygame.init()
        pygame.mixer.init()
        self.board = game.board
        self.game = game
        game.play_sound = self.play_sound
        self.controller = controller
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        self.last_squares = []
        self.hovered_square = 0
        self.holden_square = None
        self.holden_piece = None
        self.promotion_mode = False
        self.cursor_position = (0, 0)
        self.is_spectating = False
        self.show_win_screen = False
        self.sprites_cache = self.load_sprites()  # Cache the sprites
        self.font = pygame.font.Font("assets/fonts/ChessSans.ttf", 24)
        self.big_font = pygame.font.Font("assets/fonts/ChessSans.ttf", 36)
        pygame.display.set_caption("Chess Engine | Amit Sarussi")
        icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon)
        self.loop()
    
    def play_sound(self, sound_name):
        """
        Plays a sound effect based on the provided sound name.
        """
        if sound_name == "move":
            sound = pygame.mixer.Sound("assets/sounds/move.wav")
        elif sound_name == "capture":
            sound = pygame.mixer.Sound("assets/sounds/capture.wav")
        elif sound_name == "checkmate":
            sound = pygame.mixer.Sound("assets/sounds/checkmate.wav")
        elif sound_name == "game-end":
            sound = pygame.mixer.Sound("assets/sounds/game-end.wav")
        else:
            return
        sound.play()
        
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
                    if self.promotion_mode:
                        self.check_promotion_hover_square(x, y)
                        self.determine_promotion_cursor_shape()
                    
                    else:      
                        self.check_hover_square(x, y)
                        self.determine_cursor_shape()
                    
                    if self.show_win_screen:
                        self.close_button_hover()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_up()
                    
                if event.type == pygame.QUIT:
                    running = False
                
            self.draw_squares()
            self.draw_coordinates()
            self.draw_pieces()
            
            if not self.is_spectating:
                self.draw_holden_piece()
            
            if self.show_win_screen:
                self.draw_game_over()
            
            if self.promotion_mode:
                self.draw_promotion_mode()
            
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

    def draw_promotion_mode(self):
        """
        Draws the promotion mode UI, allowing the player to select a piece for promotion.
        """
        # Draw the background with a centered and rounded corner effect
        # Create the main surface with rounded corners
        surface = pygame.Surface((WINDOW_SIZE // 8, WINDOW_SIZE // 8 * 4.2), pygame.SRCALPHA)
        surface.fill((255, 255, 255))  # White background for the promotion options
        
        # Draw a simple rectangle on the surface
        rect_color = (243, 240, 243)  # Light gray color
        pygame.draw.rect(surface, rect_color, (0, WINDOW_SIZE // 8 * 4 , WINDOW_SIZE // 8, WINDOW_SIZE // 8 * 0.2))
        # Load the 'x' image
        x_image = pygame.image.load("assets/sprites/x.png")
        x_image = pygame.transform.smoothscale(x_image, (WINDOW_SIZE // 75, WINDOW_SIZE // 75))  # Scale the image

        # Calculate the position to center the 'x' image
        x_pos = (WINDOW_SIZE // 8 - x_image.get_width()) // 2
        y_pos = (WINDOW_SIZE // 8 * 4 + (WINDOW_SIZE // 8 * 0.2 - x_image.get_height()) // 2)

        # Blit the 'x' image onto the surface
        surface.blit(x_image, (x_pos, y_pos))
        
        # Draw the promotion pieces on the main surface
        for index, pce in enumerate([piece.Q, piece.N, piece.R, piece.B]):  # Only white pieces for promotion
            sprite = self.sprites_cache[pce]  # Use cached sprites for white pieces
            surface.blit(sprite, (0, index * (WINDOW_SIZE // 8)))  # Draw each piece on the surface
        
        # Blit the main surface on top of the shadow
        self.screen.blit(surface, ((self.to_square % 8) * (WINDOW_SIZE // 8), 0))
        
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
        if self.board.occupancies[color.white] & (1 << self.hovered_square) and self.is_spectating == False:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def check_promotion_hover_square(self, x, y):
        """
        Determines the chessboard square being hovered over during promotion mode
        based on the given x and y pixel coordinates, and updates the `hovered_square` attribute.
        """
        col = self.to_square % 8
        row = 7 - (self.to_square // 8)
        if x > col * (WINDOW_SIZE // 8) and x < (col + 1) * (WINDOW_SIZE // 8):
            if y > row * (WINDOW_SIZE // 8) and y < (row + 1) * (WINDOW_SIZE // 8):
                self.promotion_hover = piece.Q
            elif y > (row + 1) * (WINDOW_SIZE // 8) and y < (row + 2) * (WINDOW_SIZE // 8):
                self.promotion_hover = piece.N
            elif y > (row + 2) * (WINDOW_SIZE // 8) and y < (row + 3) * (WINDOW_SIZE // 8):
                self.promotion_hover = piece.R
            elif y > (row + 3) * (WINDOW_SIZE // 8) and y < (row + 4) * (WINDOW_SIZE // 8):
                self.promotion_hover = piece.B
            else:
                self.promotion_hover = None
        else:
            self.promotion_hover = None
    
    def determine_promotion_cursor_shape(self):
        """
        Updates the cursor shape based on the hovered square during promotion mode.
        """
        col = self.to_square % 8
        row = self.to_square // 8
        x, y = self.cursor_position
        if x > col * (WINDOW_SIZE // 8) and x < (col + 1) * (WINDOW_SIZE // 8) and y > 0 and y < WINDOW_SIZE // 8 * 4.2:
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
    
    def draw_game_over(self):
        """
        Draws a rectangle in the middle of the screen to indicate the game over state.
        """
        rect_width = WINDOW_SIZE // 3.6
        rect_height = WINDOW_SIZE // 5
        rect_x = (WINDOW_SIZE - rect_width) // 2
        rect_y = (WINDOW_SIZE - rect_height) // 2
        pygame.draw.rect(self.screen, (38, 36, 33), (rect_x, rect_y, rect_width, rect_height), border_radius=20)
        
        # Render the "Game Over" text
        if self.game.results == game_results.stalemate:
            string = "Stalemate"
        elif self.game.results == game_results.black:
            string = "Black won"
        elif self.game.results == game_results.white:
            string = "White won"
        else:
            string = "Game Over"
        text = self.big_font.render(string, True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_SIZE // 2, rect_y + rect_height // 4))
        self.screen.blit(text, text_rect)

        rect_width = WINDOW_SIZE // 3.6 * 0.8
        rect_height = 70 
        rect_x = (WINDOW_SIZE - rect_width) // 2
        rect_y = (WINDOW_SIZE - WINDOW_SIZE // 5) // 2 + WINDOW_SIZE // 5 - rect_height - 20
        pygame.draw.rect(self.screen, (141, 179, 86), (rect_x, rect_y, rect_width, rect_height), border_radius=20)
        
        # Render the "Close" text
        close_text = self.font.render("Close", True, (255, 255, 255))
        close_text_rect = close_text.get_rect(center=(WINDOW_SIZE // 2, rect_y + rect_height // 2))
        self.screen.blit(close_text, close_text_rect)
    
    def close_button_hover(self):
        """
        Checks if the mouse is hovering over the close button in the game over screen.
        """
        x, y = self.cursor_position
        rect_width = WINDOW_SIZE // 3.6 * 0.8
        rect_height = 70 
        rect_x = (WINDOW_SIZE - rect_width) // 2
        rect_y = (WINDOW_SIZE - WINDOW_SIZE // 5) // 2 + WINDOW_SIZE // 5 - rect_height - 20
        if rect_x < x < rect_x + rect_width and rect_y < y < rect_y + rect_height:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def mouse_down(self):
        """
        Handles the mouse down event for the chessboard.
        """
        if self.board.occupancies[color.white] & (1 << self.hovered_square) and self.is_spectating == False:
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
        if self.is_spectating:
            # Check if the user clicked on the close button
            x, y = self.cursor_position
            rect_width = WINDOW_SIZE // 3.6 * 0.8
            rect_height = 70
            rect_x = (WINDOW_SIZE - rect_width) // 2
            rect_y = (WINDOW_SIZE - WINDOW_SIZE // 5) // 2 + WINDOW_SIZE // 5 - rect_height - 20
            if rect_x < x < rect_x + rect_width and rect_y < y < rect_y + rect_height:
                self.show_win_screen = False
            return
        if self.promotion_mode and self.is_spectating == False:
            # Get the promoted piece
            if self.promotion_hover is not None:
                promotion = self.promotion_hover
            else:
                # Cancel move
                self.holden_square = None
                self.holden_piece = None
                self.promotion_mode = False
                return
            
            # Capture
            capture = self.board.occupancies[color.black] & (1 << self.to_square) != 0
            # Double push
            double_push = self.holden_piece == piece.P and (self.from_square - self.to_square) in (16, -16)
            # En passant
            enpassant = self.holden_piece == piece.P and (self.from_square - self.to_square) in (7, -7) and self.board.en_passant == self.to_square
            # Castling
            castling = (self.holden_piece == piece.K and (self.from_square - self.to_square) in (2, -2))
            
            # Encode the move
            move = encode_move(self.from_square, self.to_square, piece.P, promotion, capture, double_push, enpassant, castling)
            status, bots_move, game_state = self.controller.make_move(move)
            if bots_move:
                self.last_squares = [get_move_source(bots_move), get_move_target(bots_move)]
            
            if game_state != None:
                self.is_spectating = True
                self.show_win_screen = True
                        
            self.holden_square = None
            self.holden_piece = None
            self.promotion_mode = False
        elif self.is_spectating == False:
            self.last_squares = [self.holden_square]
            if self.holden_square is not None:
                self.from_square = self.holden_square
                self.to_square = self.hovered_square
                
                if self.from_square != self.to_square:
                    # Get data about the move
                    # Promotion
                    if self.promotion_mode == False:
                        if self.holden_piece == piece.P and (self.to_square // 8) == 7 and (self.from_square // 8) == 6:
                            self.promotion_mode = True
                            self.holden_square = None
                            self.holden_piece = None
                            return
                    
                    promotion = 0
                        
                    # Capture
                    capture = self.board.occupancies[color.black] & (1 << self.to_square) != 0
                    # Double push
                    double_push = self.holden_piece == piece.P and (self.from_square - self.to_square) in (16, -16)
                    # En passant
                    enpassant = self.holden_piece == piece.P and (self.from_square - self.to_square) in (7, -7) and self.board.en_passant == self.to_square
                    # Castling
                    castling = (self.holden_piece == piece.K and (self.from_square - self.to_square) in (2, -2))
                    
                    # Encode the move
                    move = encode_move(self.from_square, self.to_square, self.holden_piece, promotion, capture, double_push, enpassant, castling)
                    status, bots_move, game_state = self.controller.make_move(move)
                    if bots_move:
                        self.last_squares = [get_move_source(bots_move), get_move_target(bots_move)]
                    
                    if game_state != None:
                        self.is_spectating = True
                        self.show_win_screen = True
                        
                self.holden_square = None
                self.holden_piece = None
        