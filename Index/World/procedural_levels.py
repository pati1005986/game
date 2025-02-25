import random
import pygame

def generate_platforms(level, screen_width, screen_height):
    """
    Genera una lista de plataformas evitando superposiciones.
    Usa el rectángulo de colisión definido en la clase Platform.
    """
    platforms = []
    num_platforms = 5 + level  # Aumenta la cantidad según el nivel
    platform_width = 200
    platform_height = 5 
    margin = 50  # Margen respecto a la pantalla
    max_attempts = num_platforms * 10  # Limitar intentos
    attempts = 0

    while len(platforms) < num_platforms and attempts < max_attempts:
        x = random.randint(margin, screen_width - platform_width - margin)
        y = random.randint(screen_height // 2, screen_height - margin)
        new_rect = pygame.Rect(x, y - Platform.collision_margin, platform_width, platform_height + 2 * Platform.collision_margin)
        
        overlap = any(new_rect.colliderect(p.rect) for p in platforms)
        if not overlap:
            platforms.append(Platform(x, y, platform_width, platform_height))
        attempts += 1

    return platforms

class Platform:
    collision_margin = 10  # Margen extra para colisiones, extendido arriba y abajo

    def __init__(self, x, y, width, height):
        # self.rect extiende la zona de colisión igual en la parte superior e inferior
        self.rect = pygame.Rect(x, y - Platform.collision_margin, width, height + 2 * Platform.collision_margin)
        # La parte visual se basa en la posición original (y y height)
        self.visual_rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        # Dibuja la plataforma visualmente
        pygame.draw.rect(screen, (0, 0, 0), self.visual_rect)
