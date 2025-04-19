import random
import pygame
import math

class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visual_rect = pygame.Rect(x, y, width, height)
        self.colors = {
            'main': (101, 67, 33),      # Marrón para los bloques
            'highlight': (181, 101, 29), # Marrón claro para brillos
            'shadow': (80, 48, 20),      # Marrón oscuro para sombras
            'pattern': (139, 69, 19),    # Marrón medio para patrones
            'detail': (160, 82, 45)      # Siena para detalles
        }
        self.block_size = 16
        self.time_active = 0
        self.wave_phases = [random.random() * math.pi * 2 for _ in range(4)]
        self.glow_intensity = 0
        self.particles = []
        
    def get_spawn_position(self):
        """Returns a valid spawn position above this platform"""
        return self.rect.x + self.rect.width // 2, self.rect.y - 30

    def update(self, dt):
        """Actualiza las animaciones de la plataforma con efectos mejorados"""
        self.time_active += dt
        
        # Actualizar fases de ondulación
        for i in range(len(self.wave_phases)):
            self.wave_phases[i] += dt * (i + 1) * 0.5
        
        # Actualizar intensidad del brillo
        self.glow_intensity = (math.sin(self.time_active * 2) + 1) * 0.5
        
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
            
            particle['y'] += particle['speed'] * dt
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
        
        # Generar nuevas partículas ocasionalmente
        if random.random() < 0.02:
            self.particles.append({
                'x': random.randint(self.rect.left, self.rect.right),
                'y': self.rect.top,
                'speed': -20,  # Subir lentamente
                'lifetime': random.uniform(0.5, 1.5),
                'max_lifetime': 1.5,
                'alpha': 255
            })
    
    def draw(self, screen):
        """Dibujar plataforma con efectos visuales mejorados"""
        # Calcular ondulación para cada bloque
        num_blocks_x = self.visual_rect.width // self.block_size
        num_blocks_y = self.visual_rect.height // self.block_size
        
        # Dibujar partículas detrás de la plataforma
        for particle in self.particles:
            alpha = particle['alpha']
            color = (*self.colors['highlight'], alpha)
            pygame.draw.circle(screen, color,
                            (int(particle['x']), int(particle['y'])), 2)
        
        # Dibujar bloques con efectos
        for y in range(num_blocks_y):
            wave_height = 0
            for phase in self.wave_phases:
                wave_height += math.sin(y * 0.2 + phase) * 2
            
            for x in range(num_blocks_x):
                # Posición base del bloque
                block_x = self.visual_rect.x + x * self.block_size
                block_y = self.visual_rect.y + y * self.block_size + wave_height
                
                # Color base con variación
                base_color = self.colors['main']
                color_variation = math.sin(x * 0.3 + y * 0.2 + self.time_active) * 20
                block_color = tuple(min(255, max(0, c + color_variation)) 
                                  for c in base_color)
                
                # Dibujar bloque principal
                pygame.draw.rect(screen, block_color,
                               (block_x, block_y,
                                self.block_size, self.block_size))
                
                # Añadir detalles y patrones
                if (x + y) % 2 == 0:
                    # Patrón de cuadrícula con brillo
                    glow = self.glow_intensity * 50
                    pattern_color = tuple(min(255, c + glow)
                                       for c in self.colors['pattern'])
                    pygame.draw.rect(screen, pattern_color,
                                   (block_x + 2, block_y + 2,
                                    self.block_size - 4, self.block_size - 4))
                
                # Detalles aleatorios pero consistentes
                if hash(f"{x},{y}") % 7 == 0:
                    pygame.draw.rect(screen, self.colors['detail'],
                                   (block_x + self.block_size//4,
                                    block_y + self.block_size//4,
                                    self.block_size//2,
                                    self.block_size//2))
        
        # Efectos de borde
        self._draw_platform_edges(screen)
    
    def _draw_platform_edges(self, screen):
        """Dibujar efectos de borde de la plataforma"""
        # Borde superior con brillo dinámico
        for x in range(self.visual_rect.width):
            progress = x / self.visual_rect.width
            glow = math.sin(progress * math.pi + self.time_active * 2) * self.glow_intensity
            # Asegurar que los valores de color estén entre 0 y 255
            r = min(255, max(0, int(self.colors['highlight'][0] + glow * 100)))
            g = min(255, max(0, int(self.colors['highlight'][1] + glow * 100)))
            b = min(255, max(0, int(self.colors['highlight'][2] + glow * 100)))
            highlight_color = (r, g, b)
            
            pygame.draw.line(screen, highlight_color,
                           (self.visual_rect.x + x,
                            self.visual_rect.y),
                           (self.visual_rect.x + x + 1,
                            self.visual_rect.y))
        
        # Borde inferior con sombra dinámica
        shadow_y = self.visual_rect.y + self.visual_rect.height - 1
        pygame.draw.line(screen, self.colors['shadow'],
                       (self.visual_rect.x,
                        shadow_y),
                       (self.visual_rect.x + self.visual_rect.width,
                        shadow_y))

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
