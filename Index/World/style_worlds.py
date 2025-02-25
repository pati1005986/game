import pygame
import math
import time

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
        # Colores inspirados en auroras: tonos verdes, violetas y rosados
        self.colors = [
            (0, 255, 150),   # Verde-azulado
            (140, 0, 255),   # Violeta
            (255, 100, 150), # Rosa
            (0, 200, 255)    # Azul claro
        ]
        self.transition_speed = 0.5  # Velocidad de transición

    def get_color(self, y, height):
        """
        Calcula un color de fondo de forma continua y suave.
        Se remueve cualquier factor abrupto usando un progreso continuo de tiempo.
        """
        # Calcular un progreso continuo basado en el tiempo que recorra los colores
        progress = (time.time() * self.transition_speed) % len(self.colors)
        idx = int(progress)
        next_idx = (idx + 1) % len(self.colors)
        blend = progress - idx  # Proporción entre el color actual y el siguiente
        # Aplicar smoothstep para suavizar la transición
        smooth_blend = blend * blend * (3 - 2 * blend)
        color1 = self.colors[idx]
        color2 = self.colors[next_idx]
        r = int(color1[0] * (1 - smooth_blend) + color2[0] * smooth_blend)
        g = int(color1[1] * (1 - smooth_blend) + color2[1] * smooth_blend)
        b = int(color1[2] * (1 - smooth_blend) + color2[2] * smooth_blend)
        return (r, g, b)

def draw_gradient_background(screen):
    """Dibuja un fondo tipo aurora mezclando colores en un gradiente paralelo."""
    width, height = screen.get_size()
    aurora = AuroraColorTransition()
    for y in range(height):
        color = aurora.get_color(y, height)
        pygame.draw.line(screen, color, (0, y), (width, y))
