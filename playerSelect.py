import pygame

from headers import LIGHT_TILE

class PlayerSelect:
    """
    PlayerSelect is a class that handles the player selection screen for a chess game.
    It allows the user to choose between different player types
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        self.font_italiana = pygame.font.Font('assets/Italiana-Regular.ttf', 80)
        self.font_crimson = pygame.font.Font('assets/CrimsonText-SemiBold.ttf', 40)
        self.font_crimson_small = pygame.font.Font('assets/CrimsonText-SemiBold.ttf', 30)
        self.buttons_images = None
        self.selected = 0
        self.buttons_hover = [False, False, False, False]
        self.start_hover = False
    
    def select(self):
        """
        Runs the player selection screen, handling events, drawing UI elements,
        and returning the selected player option.
        Returns:
            int: The index of the selected player option.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    x, y = pygame.mouse.get_pos()
                    self.check_hover_buttons(x, y)
                    self.check_hover_start(x, y)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, is_hover in enumerate(self.buttons_hover):
                        if is_hover:
                            self.selected = i
                    
                    if self.start_hover:
                        running = False

                if event.type == pygame.QUIT:
                    running = False

            # Fill the background with white
            self.screen.fill((255, 255, 255))

            # Draw titles
            self.draw_titles()
            
            # Draw buttons
            self.draw_buttons()
            
            # Draw Start
            self.draw_start()

            # Flip the display
            pygame.display.flip()

        pygame.quit()
        return self.selected
    
    def draw_titles(self):
        """
        Draws the main title and subtitle on the screen.
        """
        # Create a text surface for the title
        title_surface = self.font_italiana.render('Chess Engine', True, (0, 0, 0))
        
        # Get the title rectangle and center it
        title_rect = title_surface.get_rect(center=(450, 70))
        
        # Draw the title on the screen
        self.screen.blit(title_surface, title_rect)
        
        # Create a text surface for the subtitle
        subtitle_surface = self.font_crimson.render('Amit Sarussi', True, (0, 0, 0))
        
        # Get the subtitle rectangle and center it
        subtitle_rect = subtitle_surface.get_rect(center=(450, 140))
        
        # Draw the subtitle on the screen
        self.screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_buttons(self):
        """
        Draws the player selection buttons with hover and selection effects.
        """
        texts = ["Random", "Heuristics", "Dictionary", "AI"]
        if not self.buttons_images:
            self.buttons_images = []
            for text in texts:
                button_image = pygame.image.load(f'assets/{text.lower()}.png')
                button_image = pygame.transform.smoothscale(button_image, (110, 110))
                self.buttons_images.append(button_image)
        
        for i, text in enumerate(texts):
            s = pygame.Surface((190, 190), pygame.SRCALPHA)
            s.set_alpha(128)

            pygame.draw.rect(s, LIGHT_TILE, s.get_rect(), border_radius=20)  # Adjust radius as needed
            
            if self.selected == i:
                pygame.draw.rect(
                    s,
                    (57, 38, 26),  # Border color
                    s.get_rect(),
                    width=4,
                    border_radius=20
                )  
            elif self.buttons_hover[i]:
                pygame.draw.rect(
                    s,
                    (171, 116, 79),  # Border color
                    s.get_rect(),
                    width=4,
                    border_radius=20
                )
            
            self.screen.blit(s, (30 + 216 * i, 250))
            
            # Draw the image
            self.screen.blit(self.buttons_images[i], (70 + 216 * i, 270))
            
            # Draw the text
            subtitle_surface = self.font_crimson_small.render(text, True, (70, 70, 70))
            
            # Get the subtitle rectangle and center it
            subtitle_rect = subtitle_surface.get_rect(center=(125 + 216 * i, 410))
            
            # Draw the subtitle on the screen
            self.screen.blit(subtitle_surface, subtitle_rect)
    
    def check_hover_buttons(self, x, y):
        """
        Checks if the mouse is hovering over any of the player selection buttons
        and updates the hover state.
        """
        for i in range(4):
            if x > 30 + 216 * i and x < 30 + 216 * i + 190 and y > 250 and y < 250 + 190:
                self.buttons_hover[i] = True
            else:
                self.buttons_hover[i] = False
        
        if True in self.buttons_hover:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
    def draw_start(self):
        """
        Draws the "Start" button with hover effects.
        """
        button_text = "Start"
        button_surface = self.font_crimson.render(button_text, True, (70, 70, 70))
        button_rect = button_surface.get_rect(center=(450, 530))
        
        pygame.draw.rect(
            self.screen,
            (247, 239, 225),  # Background color
            pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
            border_radius=20
        )
        pygame.draw.rect(
            self.screen,
            (199, 173, 147) if not self.start_hover else (107, 88, 76),  # Border color
            pygame.Rect(button_rect.x - 30, button_rect.y - 15, button_rect.width + 60, button_rect.height + 30),
            width=4,
            border_radius=20
        )
        
        self.screen.blit(button_surface, button_rect)
    
    def check_hover_start(self, x , y):
        """
        Checks if the mouse is hovering over the "Start" button and updates the hover state.
        """
        if x > 450 - 75 and x < 450 + 75 and y > 530 - 45 and y < 530 + 40:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.start_hover = True
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.start_hover = False
        