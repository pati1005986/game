import random
import pygame

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visual_rect = pygame.Rect(x, y, width, height)
        # Paleta de colores NES
        self.colors = {
            'main': (101, 67, 33),   # Marrón para los bloques
            'highlight': (181, 101, 29),  # Marrón claro para brillos
            'shadow': (80, 48, 20),   # Marrón oscuro para sombras
            'pattern': (139, 69, 19)  # Marrón medio para patrones
        }
        self.block_size = 16  # Tamaño de bloque estilo NES
        self.pattern_offset = 0
        
    def get_spawn_position(self):
        """Returns a valid spawn position above this platform"""
        return self.rect.x + self.rect.width // 2, self.rect.y - 30

    def draw(self, screen):
        """Dibujar plataforma con estilo retro tipo NES"""
        # Dibujar base de la plataforma
        pygame.draw.rect(screen, self.colors['main'], self.visual_rect)
        
        # Dibujar patrón de bloques
        num_blocks_x = self.visual_rect.width // self.block_size
        num_blocks_y = self.visual_rect.height // self.block_size
        
        for y in range(num_blocks_y):
            for x in range(num_blocks_x):
                block_x = self.visual_rect.x + x * self.block_size
                block_y = self.visual_rect.y + y * self.block_size
                
                # Dibujar patrón de bloques
                if (x + y) % 2 == 0:
                    pygame.draw.rect(screen, self.colors['pattern'],
                                  (block_x, block_y, self.block_size, self.block_size), 1)
                
                # Dibujar brillos en los bordes superiores
                if y == 0:
                    pygame.draw.line(screen, self.colors['highlight'],
                                  (block_x, block_y),
                                  (block_x + self.block_size, block_y))
                
                # Dibujar sombras en los bordes inferiores
                if y == num_blocks_y - 1:
                    pygame.draw.line(screen, self.colors['shadow'],
                                  (block_x, block_y + self.block_size - 1),
                                  (block_x + self.block_size, block_y + self.block_size - 1))

def generate_platforms(level, screen_width, screen_height):
    platforms = []
    platform_height = 32  # Altura ajustada para bloques de 16px
    min_platform_width = 96  # Múltiplo de 16 para alineación de bloques
    max_platform_width = 256
    
    # Plataforma base más ancha
    base_platform = Platform(0, screen_height - 80,
                           screen_width, platform_height)
    platforms.append(base_platform)
    
    # Plataformas adicionales según el nivel
    num_platforms = 2 + level
    for _ in range(num_platforms):
        # Ajustar ancho para que sea múltiplo de 16
        width = random.randint(min_platform_width // 16, max_platform_width // 16) * 16
        x = random.randint(0, (screen_width - width) // 16) * 16  # Alinear a la cuadrícula
        y = random.randint((screen_height//2) // 16, (screen_height - 150) // 16) * 16
        
        # Evitar superposición
        valid_position = True
        for p in platforms:
            if abs(y - p.rect.y) < platform_height * 2:
                if x < p.rect.right and x + width > p.rect.left:
                    valid_position = False
                    break
        
        if valid_position:
            platforms.append(Platform(x, y, width, platform_height))
    
    return platforms
