import os
import pygame
import ctypes

from headers import LIGHT_TILE

class PlayerSelect:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        self.font_italiana = pygame.font.Font('assets/fonts/Italiana.ttf', 80)
        self.font_crimson = pygame.font.Font('assets/fonts/CrimsonText.ttf', 40)
        self.font_crimson_small = pygame.font.Font('assets/fonts/CrimsonText.ttf', 30)
        self.buttons_images = None
        self.selected = 0
        self.buttons_hover = [False, False, False, False]
        self.start_hover = False
        self.rules_hover = False
        pygame.display.set_caption("Chess Engine - Player Selection")
        icon = pygame.image.load("assets/icon.png")
        pygame.display.set_icon(icon)

    def select(self) -> int:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    x, y = pygame.mouse.get_pos()
                    self.check_hover_buttons(x, y)
                    self.check_hover_start(x, y)
                    self.check_hover_rules(x, y)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, is_hover in enumerate(self.buttons_hover):
                        if is_hover:
                            self.selected = i
                    if self.start_hover:
                        running = False
                    if self.rules_hover:
                        self.show_rules_popup()

                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((255, 255, 255))
            self.draw_titles()
            self.draw_buttons()
            self.draw_start()
            self.draw_rules()

            pygame.display.flip()

        pygame.quit()
        return self.selected

    def draw_titles(self) -> None:
        title_surface = self.font_italiana.render('Chess Engine', True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(450, 70))
        self.screen.blit(title_surface, title_rect)
        subtitle_surface = self.font_crimson.render('Amit Sarussi', True, (0, 0, 0))
        subtitle_rect = subtitle_surface.get_rect(center=(450, 140))
        self.screen.blit(subtitle_surface, subtitle_rect)

    def draw_buttons(self) -> None:
        texts = ["Random", "Heuristics", "Dictionary", "AI"]
        if not self.buttons_images:
            self.buttons_images = []
            for text in texts:
                button_image = pygame.image.load(f'assets/sprites/{text.lower()}.png')
                button_image = pygame.transform.smoothscale(button_image, (110, 110))
                self.buttons_images.append(button_image)
        
        for i, text in enumerate(texts):
            s = pygame.Surface((190, 190), pygame.SRCALPHA)
            s.set_alpha(128)
            pygame.draw.rect(s, LIGHT_TILE, s.get_rect(), border_radius=20)
            if self.selected == i:
                pygame.draw.rect(s, (57, 38, 26), s.get_rect(), width=4, border_radius=20)
            elif self.buttons_hover[i]:
                pygame.draw.rect(s, (171, 116, 79), s.get_rect(), width=4, border_radius=20)
            self.screen.blit(s, (30 + 216 * i, 250))
            self.screen.blit(self.buttons_images[i], (70 + 216 * i, 270))
            subtitle_surface = self.font_crimson_small.render(text, True, (70, 70, 70))
            subtitle_rect = subtitle_surface.get_rect(center=(125 + 216 * i, 410))
            self.screen.blit(subtitle_surface, subtitle_rect)

    def check_hover_buttons(self, x, y) -> None:
        for i in range(4):
            if x > 30 + 216 * i and x < 30 + 216 * i + 190 and y > 250 and y < 250 + 190:
                self.buttons_hover[i] = True
            else:
                self.buttons_hover[i] = False
        if True in self.buttons_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def draw_start(self) -> None:
        button_text = "Start"
        button_surface = self.font_crimson.render(button_text, True, (70, 70, 70))
        button_rect = button_surface.get_rect(center=(330, 530))
        pygame.draw.rect(self.screen, (247, 239, 225),
                         pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
                         border_radius=20)
        pygame.draw.rect(self.screen,
                         (199, 173, 147) if not self.start_hover else (107, 88, 76),
                         pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
                         width=4, border_radius=20)
        self.screen.blit(button_surface, button_rect)

    def draw_rules(self) -> None:
        button_text = "Rules"
        button_surface = self.font_crimson.render(button_text, True, (70, 70, 70))
        button_rect = button_surface.get_rect(center=(570, 530))
        pygame.draw.rect(self.screen, (247, 239, 225),
                         pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
                         border_radius=20)
        pygame.draw.rect(self.screen,
                         (199, 173, 147) if not self.rules_hover else (107, 88, 76),
                         pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
                         width=4, border_radius=20)
        self.screen.blit(button_surface, button_rect)

    def check_hover_start(self, x, y) -> None:
        if 255 < x < 405 and 485 < y < 575:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.start_hover = True
        else:
            self.start_hover = False

    def check_hover_rules(self, x, y) -> None:
        if 495 < x < 645 and 485 < y < 575:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.rules_hover = True
        else:
            self.rules_hover = False

    def show_rules_popup(self) -> None:
        full_rules_1 = (
            "CHESS RULES - Part 1:\n\n"
            "1. Objective: The goal of chess is to checkmate your opponent's king. "
            "This means the king is under threat of capture ('check') and cannot escape from capture.\n\n"

            "2. Setup: Each player starts with 16 pieces — 1 King, 1 Queen, 2 Rooks, 2 Bishops, 2 Knights, and 8 Pawns. "
            "White moves first. Pieces are placed on the two closest rows (ranks) of the board. The Queen goes on her own color.\n\n"

            "3. Movement:\n"
            "  - Pawns: Move forward one square. First move can be two. Capture diagonally. "
            "Can promote to Queen, Rook, Bishop, or Knight upon reaching the 8th rank.\n"
            "  - Rooks: Move any number of squares horizontally or vertically.\n"
            "  - Bishops: Move any number of squares diagonally.\n"
            "  - Knights: Move in an L-shape: two squares in one direction and then one perpendicular. Jump over pieces.\n"
            "  - Queen: Combines the power of Rook and Bishop.\n"
            "  - King: Moves one square in any direction.\n"
        )

        full_rules_2 = (
            "CHESS RULES - Part 2:\n\n"
            "4. Special Moves:\n"
            "  - Castling: The king moves two squares toward a rook, and the rook jumps over the king. "
            "Conditions: neither has moved, path is clear, and king not in/through check.\n"
            "  - En Passant: If a pawn moves two squares forward from its starting position and lands beside an enemy pawn, "
            "that pawn may capture it 'in passing' as if it had moved only one square.\n"
            "  - Promotion: When a pawn reaches the opposite side, it must be promoted to another piece (typically a Queen).\n\n"

            "5. Check and Checkmate:\n"
            "  - Check: The king is threatened with capture. You must respond by moving the king, blocking, or capturing the threat.\n"
            "  - Checkmate: The king is in check and there is no legal move to escape. The game ends.\n\n"

            "6. Draw Conditions:\n"
            "  - Stalemate: The player has no legal move and is not in check.\n"
            "  - Insufficient material: Not enough pieces left to force checkmate (e.g., king vs. king).\n"
            "  - Threefold repetition or 50-move rule: Same position repeated 3 times or 50 moves without pawn move or capture.\n\n"

            "Enjoy the game!"
        )

        ctypes.windll.user32.MessageBoxW(0, full_rules_1, "Chess Rules (1/2)", 0)
        ctypes.windll.user32.MessageBoxW(0, full_rules_2, "Chess Rules (2/2)", 0)

