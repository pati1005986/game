import random
import pygame

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visual_rect = pygame.Rect(x, y, width, height)
        self.decorations = []
        self._generate_decorations()
        
    def _generate_decorations(self):
        # Generar decoraciones en la plataforma
        num_decorations = self.rect.width // 40
        for _ in range(num_decorations):
            x = random.randint(self.rect.left, self.rect.right - 10)
            self.decorations.append({
                'x': x,
                'type': random.choice(['grass', 'crystal']),
                'color': random.choice([
                    (34, 139, 34),  # Verde forestas
                    (50, 205, 50),  # Lima
                    (124, 252, 0),  # Verde césped
                    (147, 112, 219),  # Violeta medio
                    (138, 43, 226)   # Violeta azulado
                ])
            })

    def get_spawn_position(self):
        """Returns a valid spawn position above this platform"""
        return self.rect.x + self.rect.width // 2, self.rect.y + 20

    def draw(self, screen):
        # Dibujar la plataforma principal con gradiente
        gradient_height = self.visual_rect.height // 2
        for i in range(gradient_height):
            y = self.visual_rect.y + i
            alpha = 255 - (i * 155 // gradient_height)
            color = (40, 40, 40, alpha)  # Gris oscuro con alpha variable
            s = pygame.Surface((self.visual_rect.width, 1), pygame.SRCALPHA)
            s.fill(color)
            screen.blit(s, (self.visual_rect.x, y))
        
        # Dibujar borde superior con línea brillante
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.visual_rect.left, self.visual_rect.top),
                        (self.visual_rect.right, self.visual_rect.top), 2)
        
        # Dibujar decoraciones
        for dec in self.decorations:
            if dec['type'] == 'grass':
                # Dibujar hierba
                height = random.randint(3, 6)
                pygame.draw.line(screen, dec['color'],
                               (dec['x'], self.visual_rect.top),
                               (dec['x'], self.visual_rect.top - height), 2)
            else:  # crystal
                # Dibujar cristal
                points = [
                    (dec['x'], self.visual_rect.top - 8),
                    (dec['x'] - 3, self.visual_rect.top),
                    (dec['x'] + 3, self.visual_rect.top)
                ]
                pygame.draw.polygon(screen, dec['color'], points)

def generate_platforms(level, screen_width, screen_height):
    platforms = []
    platform_height = 25  # Altura aumentada para más detalle
    platform_y = screen_height - 80
    
    # Create a single floor platform that spans the width of the screen
    floor = Platform(0, platform_y, screen_width, platform_height)
    platforms.append(floor)
    
    return platforms
