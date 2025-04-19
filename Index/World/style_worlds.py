import pygame
import math
import time
import random
from typing import List, Tuple, Dict

class RetroBackground:
    _instance = None  # Singleton instance
    
    def __new__(cls, screen_width: int, screen_height: int):
        """Implementación Singleton para evitar múltiples instancias"""
        if cls._instance is None:
            cls._instance = super(RetroBackground, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, screen_width: int, screen_height: int):
        """Inicializa el fondo retro con gradiente y estrellas mejoradas."""
        if self._initialized:
            return
            
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Paleta de colores NES extendida para gradiente más suave
        self.colors = [
            (0, 0, 0),       # Negro
            (0, 0, 52),      # Azul muy oscuro
            (0, 0, 92),      # Azul oscuro
            (0, 0, 140),     # Azul medio
            (0, 0, 188),     # Azul claro
            (20, 20, 255)    # Azul brillante
        ]
        
        # Pre-calcular colores interpolados para el gradiente
        self.gradient_colors = self._generate_gradient_colors()
        
        # Configuración mejorada de estrellas
        self.scroll_speed = 15
        self.star_layers = [
            {'count': 30, 'size': 1, 'speed': 0.2, 'color': (255, 255, 255), 'trail_length': 0},
            {'count': 20, 'size': 2, 'speed': 0.3, 'color': (200, 200, 255), 'trail_length': 2},
            {'count': 15, 'size': 3, 'speed': 0.4, 'color': (170, 170, 255), 'trail_length': 3}
        ]
        
        # Crear superficie de caché para el gradiente
        self.gradient_surface = self._create_gradient_surface()
        
        # Inicializar estrellas con trails
        self.stars = self._init_stars()
        self.star_trails: List[Dict] = []
        
        # Cache para las superficies de las estrellas
        self.star_surfaces = self._create_star_surfaces()
        
        self._initialized = True

    def _generate_gradient_colors(self) -> List[Tuple[int, int, int]]:
        """Genera una lista de colores interpolados para un gradiente más suave"""
        gradient_colors = []
        steps = self.screen_height
        
        for i in range(steps):
            progress = i / (steps - 1)
            index = progress * (len(self.colors) - 1)
            index_low = int(index)
            index_high = min(index_low + 1, len(self.colors) - 1)
            blend = index - index_low
            
            c1 = self.colors[index_low]
            c2 = self.colors[index_high]
            
            color = tuple(int(c1[j] * (1 - blend) + c2[j] * blend) for j in range(3))
            gradient_colors.append(color)
            
        return gradient_colors

    def _create_gradient_surface(self) -> pygame.Surface:
        """Crea una superficie pre-renderizada con el gradiente"""
        surface = pygame.Surface((self.screen_width, self.screen_height))
        
        for y, color in enumerate(self.gradient_colors):
            pygame.draw.line(surface, color, (0, y), (self.screen_width, y))
            
        return surface

    def _create_star_surfaces(self) -> Dict[int, pygame.Surface]:
        """Crea superficies pre-renderizadas para las estrellas"""
        surfaces = {}
        for layer in self.star_layers:
            size = layer['size']
            if size not in surfaces:
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 255, 255), (size//2, size//2), size//2)
                surfaces[size] = surf
        return surfaces

    def _init_stars(self) -> List[Dict]:
        """Inicializa las estrellas con efectos mejorados"""
        stars = []
        for layer in self.star_layers:
            for _ in range(layer['count']):
                stars.append({
                    'x': random.randint(0, self.screen_width),
                    'y': random.randint(0, self.screen_height),
                    'size': layer['size'],
                    'speed': layer['speed'],
                    'color': layer['color'],
                    'blink_offset': random.random() * 6.28,
                    'trail_length': layer['trail_length'],
                    'trail': []
                })
        return stars

    def update(self, dt: float) -> None:
        """Actualiza las animaciones del fondo con efectos mejorados"""
        current_time = time.time()
        
        # Actualizar estrellas con paralaje
        for star in self.stars:
            # Aplicar paralaje basado en el tamaño (las estrellas más grandes se mueven más rápido)
            parallax_factor = star['size'] / 3
            
            # Actualizar posición con movimiento sinusoidal suave
            prev_x = star['x']
            star['x'] = (star['x'] - star['speed'] * self.scroll_speed * dt * parallax_factor) % self.screen_width
            star['y'] += math.sin(current_time + star['blink_offset']) * 0.5 * dt
            
            # Mantener las estrellas dentro de la pantalla
            star['y'] = star['y'] % self.screen_height
            
            # Actualizar trail con desvanecimiento
            if star['trail_length'] > 0:
                star['trail'].insert(0, (prev_x, star['y']))
                if len(star['trail']) > star['trail_length']:
                    star['trail'].pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja el fondo con efectos mejorados"""
        # Dibujar gradiente con efecto de ondulación
        t = time.time()
        wave_offset = math.sin(t * 0.5) * 2
        
        for y, color in enumerate(self.gradient_colors):
            # Aplicar ondulación al gradiente
            wave = math.sin(y * 0.01 + t) * wave_offset
            pygame.draw.line(screen, color, 
                           (0 + wave, y),
                           (self.screen_width + wave, y))
        
        # Dibujar estrellas con efectos mejorados
        for star in self.stars:
            # Calcular brillo con parpadeo suave
            blink = (math.sin(t * 2 + star['blink_offset']) + 1) * 0.5
            glow = (math.sin(t * 3) + 1) * 0.3
            alpha = int(255 * (blink + glow))
            
            # Dibujar trail con desvanecimiento gradual
            if star['trail']:
                points = [(star['x'], star['y'])] + star['trail']
                for i in range(len(points) - 1):
                    fade = 1 - (i / len(points))
                    color = (*star['color'][:3], int(alpha * fade * 0.5))
                    start = points[i]
                    end = points[i + 1]
                    pygame.draw.line(screen, color, start, end, 1)
            
            # Dibujar estrella con efecto de brillo
            base_size = star['size']
            glow_size = base_size * (1.5 + math.sin(t * 4 + star['blink_offset']) * 0.2)
            
            # Dibujar resplandor
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_color = (*star['color'][:3], int(alpha * 0.3))
            pygame.draw.circle(glow_surf, glow_color,
                            (glow_size, glow_size), glow_size)
            screen.blit(glow_surf,
                       (star['x'] - glow_size,
                        star['y'] - glow_size))
            
            # Dibujar estrella central
            star_surf = self.star_surfaces[base_size].copy()
            star_surf.set_alpha(alpha)
            screen.blit(star_surf,
                       (star['x'] - base_size/2,
                        star['y'] - base_size/2))

def draw_gradient_background(screen: pygame.Surface) -> None:
    """Función de compatibilidad para dibujar el fondo retro."""
    width, height = screen.get_size()
    # Usar singleton para evitar recrear el fondo
    background = RetroBackground(width, height)
    background.update(1/60)
    background.draw(screen)
