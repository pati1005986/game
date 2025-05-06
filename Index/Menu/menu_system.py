import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MENU_BG = (0, 0, 92)        # Azul oscuro para fondo
MENU_TEXT = (255, 255, 255)  # Blanco para texto
MENU_SELECT = (255, 255, 0)  # Amarillo para selección

# Available screen resolutions
SCREEN_RESOLUTIONS = [
    (800, 450),
    (1024, 576),
    (1280, 720),
    (1920, 1080)
]

class Button:
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.selected = False
        
    def draw(self, screen):
        color = MENU_SELECT if self.selected else MENU_TEXT
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.selected = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.update_dimensions()

        # Crear botones centrados
        self.buttons = {
            'play': Button(self.screen_width // 2 - self.button_width // 2,
                           self.start_y,
                           self.button_width, self.button_height, "JUGAR"),
            'settings': Button(self.screen_width // 2 - self.button_width // 2,
                               self.start_y + self.button_height + self.button_spacing,
                               self.button_width, self.button_height, "AJUSTES")
        }

        # Título del juego
        self.title_font = pygame.font.SysFont(None, 72)
        self.title_text = "MI JUEGO"

    def update_dimensions(self):
        """Update dimensions for responsive design."""
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.button_width = min(200, self.screen_width * 0.4)
        self.button_height = min(50, self.screen_height * 0.1)
        self.button_spacing = min(20, self.screen_height * 0.04)
        self.start_y = self.screen_height // 2 - self.button_height

    def draw(self, background_func):
        # Dibujar fondo
        background_func(self.screen)

        # Dibujar título
        title_surface = self.title_font.render(self.title_text, True, WHITE)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        self.screen.blit(title_surface, title_rect)

        # Dibujar botones
        for button in self.buttons.values():
            button.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE:
            pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            self.update_dimensions()
            for name, button in self.buttons.items():
                button.rect.width = self.button_width
                button.rect.height = self.button_height
                button.rect.x = self.screen_width // 2 - self.button_width // 2
                button.rect.y = self.start_y if name == 'play' else self.start_y + self.button_height + self.button_spacing

        for name, button in self.buttons.items():
            if button.handle_event(event):
                return name
        return None

class Settings:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.scroll_y = 0
        self.scroll_speed = 20
        self.visible_area = pygame.Rect(0, 100, screen.get_width(), screen.get_height() - 200)
        
        # Dimensiones básicas
        self.button_width = min(200, screen.get_width() * 0.4)
        self.button_height = min(50, screen.get_height() * 0.1)
        self.button_spacing = min(20, screen.get_height() * 0.04)
        
        # Contenedor virtual para todos los elementos
        self.elements = []
        
        # Título y subtítulos
        title_y = 50
        self.title_pos = (screen.get_width()//2, title_y)
        
        # Iniciar desde después del título
        current_y = title_y + 100
        
        # Sección de Resoluciones
        self.resolution_label_pos = (screen.get_width()//2, current_y)
        current_y += 50
        
        # Botones de resolución
        self.resolution_buttons = []
        self.current_resolution_index = 0
        
        for i, (width, height) in enumerate(SCREEN_RESOLUTIONS):
            text = f"{width}x{height}"
            button = Button(screen.get_width()//2 - self.button_width//2,
                          current_y,
                          self.button_width, self.button_height, text)
            self.resolution_buttons.append(button)
            self.elements.append(button)
            current_y += self.button_height + self.button_spacing
            
            if (width, height) == (screen.get_width(), screen.get_height()):
                self.current_resolution_index = i

        # Sección de Dificultad
        self.difficulty_label_pos = (screen.get_width()//2, current_y)
        current_y += 50
        
        # Botones de dificultad
        self.difficulties = ['FÁCIL', 'NORMAL', 'DIFÍCIL']
        self.difficulty_buttons = []
        self.current_difficulty = 1  # Normal por defecto
        
        for i, diff in enumerate(self.difficulties):
            button = Button(screen.get_width()//2 - self.button_width//2,
                          current_y,
                          self.button_width, self.button_height, diff)
            self.difficulty_buttons.append(button)
            self.elements.append(button)
            current_y += self.button_height + self.button_spacing

        # Botón de pantalla completa
        self.fullscreen_button = Button(screen.get_width()//2 - self.button_width//2,
                                      current_y,
                                      self.button_width, self.button_height,
                                      "PANTALLA COMPLETA: NO")
        self.elements.append(self.fullscreen_button)
        current_y += self.button_height + self.button_spacing
        
        self.is_fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
        if self.is_fullscreen:
            self.fullscreen_button.text = "PANTALLA COMPLETA: SÍ"
        
        # Botón de volver (siempre visible en la parte inferior)
        self.back_button = Button(screen.get_width()//2 - self.button_width//2,
                                screen.get_height() - self.button_height - self.button_spacing,
                                self.button_width, self.button_height, "VOLVER")
        
        # Calcular altura total del contenido y máximo scroll
        self.content_height = current_y - title_y
        self.max_scroll = max(0, self.content_height - (self.visible_area.height))
        
    def handle_scroll(self, event):
        if event.type == pygame.MOUSEWHEEL:
            # Invertir la dirección del scroll
            self.scroll_y = max(0, min(self.scroll_y - event.y * self.scroll_speed, self.max_scroll))
            
            # Actualizar posiciones de los elementos
            for element in self.elements:
                element.rect.y = element.rect.y + event.y * self.scroll_speed
                
    def draw(self, background_func):
        # Dibujar fondo
        background_func(self.screen)
        
        # Dibujar título (fijo)
        title = self.font.render("AJUSTES", True, WHITE)
        title_rect = title.get_rect(center=self.title_pos)
        self.screen.blit(title, title_rect)
        
        # Configurar scissor para el área visible
        pygame.display.get_surface().set_clip(self.visible_area)
        
        # Dibujar subtítulo de resolución
        resolution_label = self.font.render("RESOLUCIÓN DE PANTALLA", True, WHITE)
        resolution_rect = resolution_label.get_rect(center=(self.resolution_label_pos[0],
                                                          self.resolution_label_pos[1] - self.scroll_y))
        if self.visible_area.colliderect(resolution_rect):
            self.screen.blit(resolution_label, resolution_rect)
        
        # Dibujar subtítulo de dificultad
        difficulty_label = self.font.render("DIFICULTAD", True, WHITE)
        difficulty_rect = difficulty_label.get_rect(center=(self.difficulty_label_pos[0],
                                                          self.difficulty_label_pos[1] - self.scroll_y))
        if self.visible_area.colliderect(difficulty_rect):
            self.screen.blit(difficulty_label, difficulty_rect)
        
        # Dibujar botones de resolución
        for i, button in enumerate(self.resolution_buttons):
            button_rect = button.rect.copy()
            button_rect.y -= self.scroll_y
            
            if self.visible_area.colliderect(button_rect):
                if i == self.current_resolution_index and not self.is_fullscreen:
                    pygame.draw.rect(self.screen, MENU_SELECT, 
                                   button_rect.inflate(20, 10), 2)
                button.rect = button_rect
                button.draw(self.screen)
        
        # Dibujar botones de dificultad
        for i, button in enumerate(self.difficulty_buttons):
            button_rect = button.rect.copy()
            button_rect.y -= self.scroll_y
            
            if self.visible_area.colliderect(button_rect):
                if i == self.current_difficulty:
                    pygame.draw.rect(self.screen, MENU_SELECT,
                                   button_rect.inflate(20, 10), 2)
                button.rect = button_rect
                button.draw(self.screen)
        
        # Dibujar botón de pantalla completa
        fullscreen_rect = self.fullscreen_button.rect.copy()
        fullscreen_rect.y -= self.scroll_y
        if self.visible_area.colliderect(fullscreen_rect):
            if self.is_fullscreen:
                pygame.draw.rect(self.screen, MENU_SELECT,
                               fullscreen_rect.inflate(20, 10), 2)
            self.fullscreen_button.rect = fullscreen_rect
            self.fullscreen_button.draw(self.screen)
        
        # Restaurar el área de recorte
        pygame.display.get_surface().set_clip(None)
        
        # Dibujar botón de volver (siempre visible)
        self.back_button.draw(self.screen)
        
        # Dibujar indicadores de scroll si es necesario
        if self.max_scroll > 0:
            if self.scroll_y > 0:
                # Flecha arriba
                pygame.draw.polygon(self.screen, WHITE, [
                    (self.screen.get_width()//2, 110),
                    (self.screen.get_width()//2 - 10, 120),
                    (self.screen.get_width()//2 + 10, 120)
                ])
            
            if self.scroll_y < self.max_scroll:
                # Flecha abajo
                pygame.draw.polygon(self.screen, WHITE, [
                    (self.screen.get_width()//2, self.screen.get_height() - 130),
                    (self.screen.get_width()//2 - 10, self.screen.get_height() - 140),
                    (self.screen.get_width()//2 + 10, self.screen.get_height() - 140)
                ])
        
    def handle_event(self, event):
        # Manejar scroll
        if event.type == pygame.MOUSEWHEEL:
            self.handle_scroll(event)
            return None, None
            
        # Manejar botón de volver (siempre visible)
        if self.back_button.handle_event(event):
            return 'menu', None
            
        # Ajustar posición Y para la detección de eventos
        mouse_pos = pygame.mouse.get_pos()
        
        # Manejar botones de resolución
        if not self.is_fullscreen:
            for i, button in enumerate(self.resolution_buttons):
                button_rect = button.rect.copy()
                button_rect.y -= self.scroll_y
                if self.visible_area.colliderect(button_rect):
                    if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(mouse_pos):
                        if i != self.current_resolution_index:
                            self.current_resolution_index = i
                            return 'change_resolution', SCREEN_RESOLUTIONS[i]
        
        # Manejar botones de dificultad
        for i, button in enumerate(self.difficulty_buttons):
            button_rect = button.rect.copy()
            button_rect.y -= self.scroll_y
            if self.visible_area.colliderect(button_rect):
                if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(mouse_pos):
                    if i != self.current_difficulty:
                        self.current_difficulty = i
                        return 'change_difficulty', i
        
        # Manejar botón de pantalla completa
        fullscreen_rect = self.fullscreen_button.rect.copy()
        fullscreen_rect.y -= self.scroll_y
        if self.visible_area.colliderect(fullscreen_rect):
            if event.type == pygame.MOUSEBUTTONDOWN and fullscreen_rect.collidepoint(mouse_pos):
                self.is_fullscreen = not self.is_fullscreen
                self.fullscreen_button.text = "PANTALLA COMPLETA: SÍ" if self.is_fullscreen else "PANTALLA COMPLETA: NO"
                return 'toggle_fullscreen', None
        
        return None, None

def change_screen_resolution(screen, new_resolution):
    return pygame.display.set_mode(new_resolution)