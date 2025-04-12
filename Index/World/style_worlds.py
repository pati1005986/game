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
        # Nuevos colores más vibrantes para el fondo
        self.colors = [
            (41, 128, 185),   # Azul océano
            (142, 68, 173),   # Púrpura místico
            (52, 152, 219),   # Azul cielo
            (155, 89, 182),   # Violeta suave
            (26, 188, 156),   # Turquesa
            (46, 204, 113)    # Esmeralda
        ]
        self.transition_speed = 0.5  # Velocidad de transición
        
        # Añadir efectos de partículas
        self.particles = []
        self.max_particles = 50
        self.init_particles()

    def init_particles(self):
        """Inicializar partículas decorativas"""
        for _ in range(self.max_particles):
            self.particles.append({
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'speed': random.uniform(0.5, 2),
                'size': random.randint(2, 5),
                'alpha': random.randint(50, 200)
            })

    def update_particles(self, dt):
        """Actualizar posición de partículas"""
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -10:
                p['y'] = 610
                p['x'] = random.randint(0, 800)

    def get_color(self, y, height):
        """Mejorar la generación de colores con más variación"""
        progress = (time.time() * self.transition_speed) % len(self.colors)
        idx = int(progress)
        next_idx = (idx + 1) % len(self.colors)
        
        # Añadir variación de color basada en la posición Y
        y_factor = y / height
        blend = (math.sin(progress - idx + y_factor) + 1) / 2
        
        color1 = self.colors[idx]
        color2 = self.colors[next_idx]
        
        # Añadir efecto de ondulación
        wave = math.sin(y * 0.02 + time.time()) * 0.1
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
    
    # Dibujar gradiente base
    for y in range(height):
        color = aurora.get_color(y, height)
        pygame.draw.line(screen, color, (0, y), (width, y))
    
    # Actualizar y dibujar partículas
    aurora.update_particles(1/60)  # Asumiendo 60 FPS
    for p in aurora.particles:
        color = aurora.get_color(p['y'], height)
        s = pygame.Surface((p['size'], p['size']))
        s.fill(color)
        s.set_alpha(p['alpha'])
        screen.blit(s, (p['x'], p['y']))
    
    # Añadir efecto de destello
    current_time = time.time()
    for i in range(3):
        flash_pos = (
            width/2 + math.sin(current_time * 0.5 + i*2.1) * width/3,
            height/2 + math.cos(current_time * 0.3 + i*1.7) * height/3
        )
        radius = (math.sin(current_time + i) + 1) * 50 + 20
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*aurora.get_color(int(flash_pos[1]), height), 30), 
                         (radius, radius), radius)
        screen.blit(s, (flash_pos[0]-radius, flash_pos[1]-radius))
