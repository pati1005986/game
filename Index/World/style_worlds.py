import pygame
import math
import time
import random

class ColorTransition:
    def __init__(self):
        self.start_time = time.time()
        self.color_combinations = [
            ((255, 255, 255), (128, 128, 128)),  # White to Gray
            ((255, 200, 200), (128, 100, 100)),  # Pink to Dark Pink
            ((200, 255, 200), (100, 128, 100)),  # Green to Dark Green
            ((200, 200, 255), (100, 100, 128))   # Blue to Dark Blue
        ]
        self.current_index = 0
        self.transition_duration = 5.0  # Seconds per transition

    def get_colors(self):
        elapsed = time.time() - self.start_time
        t = (math.sin(elapsed * (math.pi / self.transition_duration)) + 1) / 2
        
        idx1 = self.current_index
        idx2 = (self.current_index + 1) % len(self.color_combinations)
        
        color1_start, color1_end = self.color_combinations[idx1]
        color2_start, color2_end = self.color_combinations[idx2]
        
        # Interpolate between color combinations
        start_color = (
            int(color1_start[0] * (1 - t) + color2_start[0] * t),
            int(color1_start[1] * (1 - t) + color2_start[1] * t),
            int(color1_start[2] * (1 - t) + color2_start[2] * t)
        )
        end_color = (
            int(color1_end[0] * (1 - t) + color2_end[0] * t),
            int(color1_end[1] * (1 - t) + color2_end[1] * t),
            int(color1_end[2] * (1 - t) + color2_end[2] * t)
        )
        
        # Switch to next combination when transition is complete
        if t >= 0.99:
            self.current_index = idx2
            self.start_time = time.time()
            
        return start_color, end_color

class AuroraColorTransition:
    def __init__(self):
        self.start_time = time.time()
        # Paleta de colores más vibrante y armoniosa
        self.colors = [
            (25, 25, 112),    # Azul medianoche
            (72, 61, 139),    # Púrpura oscuro
            (106, 90, 205),   # Púrpura azulado
            (123, 104, 238),  # Púrpura medio
            (147, 112, 219),  # Violeta medio
            (138, 43, 226)    # Violeta azulado
        ]
        self.transition_speed = 0.3
        self.particles = []
        self.stars = []  # Nuevas estrellas para el fondo
        self.max_particles = 70  # Más partículas
        self.max_stars = 100
        self.init_particles()
        self.init_stars()

    def init_stars(self):
        """Inicializar estrellas en el fondo"""
        for _ in range(self.max_stars):
            self.stars.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 450),
                'size': random.randint(1, 3),
                'twinkle_speed': random.uniform(1.0, 3.0),
                'offset': random.uniform(0, 6.28)  # 2*pi para fase aleatoria
            })

    def init_particles(self):
        """Inicializar partículas con más variedad"""
        for _ in range(self.max_particles):
            self.particles.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 450),
                'speed': random.uniform(0.2, 1.5),
                'size': random.randint(2, 6),
                'alpha': random.randint(30, 180),
                'color_shift': random.uniform(0, 1)
            })

    def update_particles(self, dt):
        """Actualizar partículas con movimiento más suave"""
        current_time = time.time()
        for p in self.particles:
            # Movimiento ondulatorio
            p['x'] += math.sin(current_time * p['speed']) * 0.5
            p['y'] -= p['speed']
            if p['y'] < -10:
                p['y'] = 460
                p['x'] = random.randint(0, 800)

    def get_color(self, y, height):
        """Color generation con más variación y suavidad"""
        progress = (time.time() * self.transition_speed) % len(self.colors)
        idx = int(progress)
        next_idx = (idx + 1) % len(self.colors)
        
        y_factor = y / height
        blend = (math.sin(progress - idx + y_factor * 2) + 1) / 2
        
        color1 = self.colors[idx]
        color2 = self.colors[next_idx]
        
        # Añadir ondulación más pronunciada
        wave = math.sin(y * 0.03 + time.time() * 0.5) * 0.15
        blend = max(0, min(1, blend + wave))
        
        return (
            int(color1[0] * (1 - blend) + color2[0] * blend),
            int(color1[1] * (1 - blend) + color2[1] * blend),
            int(color1[2] * (1 - blend) + color2[2] * blend)
        )

def draw_gradient_background(screen):
    """Dibuja un fondo mejorado con efectos"""
    width, height = screen.get_size()
    aurora = AuroraColorTransition()
    
    # Fondo base negro
    screen.fill((5, 5, 15))
    
    # Dibujar estrellas
    current_time = time.time()
    for star in aurora.stars:
        # Efecto de parpadeo
        brightness = (math.sin(current_time * star['twinkle_speed'] + star['offset']) + 1) / 2
        alpha = int(100 + brightness * 155)
        color = (255, 255, 255, alpha)
        
        s = pygame.Surface((star['size'], star['size']), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (star['size']//2, star['size']//2), star['size']//2)
        screen.blit(s, (star['x'], star['y']))
    
    # Dibujar aurora (gradiente)
    for y in range(height):
        color = aurora.get_color(y, height)
        s = pygame.Surface((width, 1), pygame.SRCALPHA)
        s.fill((*color, 100))  # Menos opaco para ver las estrellas
        screen.blit(s, (0, y))
    
    # Actualizar y dibujar partículas
    aurora.update_particles(1/60)
    for p in aurora.particles:
        color = aurora.get_color(int(p['y']), height)
        # Ajustar color con el color_shift individual
        adjusted_color = (
            min(255, int(color[0] * (1 + p['color_shift'] * 0.5))),
            min(255, int(color[1] * (1 + p['color_shift'] * 0.5))),
            min(255, int(color[2] * (1 + p['color_shift'] * 0.5)))
        )
        s = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
        s.fill((*adjusted_color, p['alpha']))
        screen.blit(s, (p['x'], p['y']))
