import pygame
import math
import time

class RetroBackground:
    def __init__(self):
        # Paleta de colores NES
        self.colors = [
            (0, 0, 0),       # Negro
            (0, 0, 92),      # Azul oscuro
            (0, 0, 140),     # Azul medio
            (0, 0, 188)      # Azul claro
        ]
        self.stars = []
        self.scroll_offset = 0
        self.scroll_speed = 15
        self.star_layers = [
            {'count': 50, 'size': 1, 'speed': 0.2, 'color': (255, 255, 255)},
            {'count': 30, 'size': 2, 'speed': 0.3, 'color': (200, 200, 255)},
            {'count': 20, 'size': 3, 'speed': 0.4, 'color': (170, 170, 255)}
        ]
        self._init_stars()
        
    def _init_stars(self):
        """Inicializar capas de estrellas con diferentes profundidades"""
        import random
        self.stars = []
        for layer in self.star_layers:
            for _ in range(layer['count']):
                self.stars.append({
                    'x': random.randint(0, 800),
                    'y': random.randint(0, 450),
                    'size': layer['size'],
                    'speed': layer['speed'],
                    'color': layer['color'],
                    'blink_offset': random.random() * 6.28
                })

    def update(self, dt):
        """Actualizar posición de las estrellas"""
        self.scroll_offset = (self.scroll_offset + self.scroll_speed * dt) % 800
        for star in self.stars:
            star['x'] = (star['x'] - star['speed'] * self.scroll_speed * dt) % 800

def draw_gradient_background(screen):
    """Dibuja un fondo estilo retro con gradiente simple y estrellas"""
    width, height = screen.get_size()
    background = RetroBackground()
    
    # Dibujar gradiente vertical con colores limitados (estilo NES)
    segment_height = height // len(background.colors)
    for i, color in enumerate(background.colors):
        pygame.draw.rect(screen, color,
                        (0, i * segment_height,
                         width, segment_height))
    
    # Actualizar y dibujar estrellas
    current_time = time.time()
    background.update(1/60)
    
    # Dibujar estrellas con parpadeo simple
    for star in background.stars:
        blink = abs(math.sin(current_time * 2 + star['blink_offset']))
        color = tuple(int(c * blink) for c in star['color'])
        pygame.draw.rect(screen, color,
                        (star['x'], star['y'],
                         star['size'], star['size']))
