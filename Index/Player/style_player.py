import pygame
import math
import time
import random
from typing import Dict, List, Tuple

class PlayerStyle:
    def __init__(
        self,
        base_color: Tuple[int, int, int] = (34, 177, 76),  # Verde claro
        accent_color: Tuple[int, int, int] = (181, 230, 29),  # Verde más claro
        pixel_size: int = 8
    ):
        self.colors = {
            'X': base_color,        # Color base del personaje
            'A': accent_color,      # Detalles del personaje
            'B': (139, 69, 19),    # Marrón para detalles
            'W': (255, 255, 255),   # Blanco para efectos
            'G': (200, 255, 200),   # Verde brillante para efectos
            ' ': None              # Transparente
        }
        
        self.pixel_size = pixel_size
        self.width = 32
        self.height = 32
        self.animation_blend_time = 0.1
        self.current_blend = 0
        self.previous_animation = 'idle'
        self.animation_offset_y = 0
        self.squash_stretch = 1.0
        self.glow_intensity = 0
        self.shake_offset = 0
        self.time_active = 0
        self.particles = []
        self.trail_points = []
        self.max_trail_points = 5
        
        self.animations = {
            "idle": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXAAAAXX ",
                  " XWXXXXWX ",
                  " XXXXXXXX ",
                  "  BBBBBB  ",
                  " XXXXXXXX ",
                  " XX XX XX " ],
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXAAAAXX ",
                  " XWXXXXWX ",
                  " XXXXXXXX ",
                  "  BBBBBB  ",
                  " XXXXXXXX ",
                  "  XXBBXX  " ]
            ],
            "run": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXAAAAXX ",
                  " XWXXXXWX ",
                  " XXXXXXXX ",
                  "  BBBBBB  ",
                  "  XXXXXX  ",
                  " XX    XX " ],
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXAAAAXX ",
                  " XWXXXXWX ",
                  " XXXXXXXX ",
                  "  BBBBBB  ",
                  " XX  XX   ",
                  "XX    XX  " ]
            ],
            "jump": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXAAAAXX ",
                  " XWXXXXWX ",
                  " XXXXXXXX ",
                  "  BBBBBB  ",
                  " XXXXXXXX ",
                  "XX    XXX " ]
            ],
            "attack": [
                [ "    WWWW   ",
                  "   WWWWWW  ",
                  "  XXAAAAXX ",
                  " XXWXXXXWXX",
                  " XXXXXXXXX ",
                  "  BBBBBB  ",
                  " XXXXXXX  ",
                  "XX    XX  " ],
                [ "   WWWW    ",
                  "  WWWWWW   ",
                  " XXAAAAXX  ",
                  "XXWXXXXWXX ",
                  "XXXXXXXXX  ",
                  " BBBBBB   ",
                  "XXXXXXX   ",
                  " XX  XX   " ]
            ]
        }
        
        self.animation_speeds = {
            'idle': 0.5,
            'run': 0.15,
            'jump': 0.2,
            'attack': 0.1
        }
        
        self.current_animation = 'idle'
        self.current_frame = 0
        self.time_since_last_frame = 0
        self.parsed_frames_cache = {}

    def update_animation(self, dt, moving=False, jumping=False, attacking=False):
        self.time_active += dt
        
        # Determinar nueva animación y asegurar que la animación de movimiento tenga prioridad correcta
        if attacking:
            new_animation = 'attack'
        elif jumping:
            new_animation = 'jump'
        elif moving:
            new_animation = 'run'
        else:
            new_animation = 'idle'
        
        # Manejar transición suave entre animaciones
        if new_animation != self.current_animation:
            self.previous_animation = self.current_animation
            self.current_animation = new_animation
            self.current_blend = self.animation_blend_time
            # Resetear el frame actual al cambiar de animación
            self.current_frame = 0
            self.time_since_last_frame = 0
        
        # Actualizar blend
        if self.current_blend > 0:
            self.current_blend = max(0, self.current_blend - dt)
        
        # Actualizar frame actual usando la velocidad específica de la animación
        frames = self.animations[self.current_animation]
        if len(frames) > 1:
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= self.animation_speeds[self.current_animation]:
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.time_since_last_frame = 0
                
        # Actualizar efectos visuales
        self.glow_intensity = (math.sin(self.time_active * 3) + 1) * 0.5
        
        # Efectos de squash y stretch más pronunciados durante el movimiento
        if jumping:
            self.squash_stretch = 1.2
        elif moving:
            self.squash_stretch = 1.0 + math.sin(self.time_active * 12) * 0.15  # Aumentado el efecto
        else:
            self.squash_stretch = 1.0 + math.sin(self.time_active * 2) * 0.05

        # Actualizar partículas
        self._update_particles(dt, attacking, moving)

    def _update_particles(self, dt, attacking, moving):
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
            
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
        
        # Generar partículas según el estado
        if attacking and random.random() < 0.3:
            self._spawn_attack_particles()
        elif moving and random.random() < 0.2:
            self._spawn_movement_particles()

    def _spawn_attack_particles(self):
        for _ in range(3):
            angle = random.uniform(-math.pi/4, math.pi/4)
            speed = random.uniform(100, 200)
            self.particles.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.uniform(0.2, 0.4),
                'max_lifetime': 0.4,
                'alpha': 255,
                'type': 'attack'
            })

    def _spawn_movement_particles(self):
        self.particles.append({
            'x': random.uniform(-5, 5),
            'y': self.height,
            'vx': random.uniform(-20, 20),
            'vy': random.uniform(-50, -20),
            'lifetime': random.uniform(0.3, 0.6),
            'max_lifetime': 0.6,
            'alpha': 255,
            'type': 'movement'
        })

    def draw(self, screen, x, y):
        # Aplicar transformaciones
        draw_x = x + self.shake_offset
        draw_y = y
        scaled_height = self.height * self.squash_stretch
        height_diff = scaled_height - self.height
        draw_y -= height_diff
        
        # Dibujar partículas
        for particle in self.particles:
            if particle['type'] == 'attack':
                color = (*self.colors['W'][:3], particle['alpha'])
            else:
                color = (*self.colors['G'][:3], particle['alpha'])
            
            pos = (int(draw_x + particle['x']), int(draw_y + particle['y']))
            size = 3 if particle['type'] == 'attack' else 2
            pygame.draw.circle(screen, color, pos, size)
        
        # Dibujar sprite principal con manejo seguro de frames
        frames = self.animations[self.current_animation]
        if not frames:  # Safety check for empty animation
            return
            
        self.current_frame = self.current_frame % len(frames)  # Ensure valid frame index
        current_frame = frames[self.current_frame]
        
        # Si hay una transición en curso, mezclar con el frame anterior
        if self.current_blend > 0 and self.previous_animation in self.animations:
            prev_frames = self.animations[self.previous_animation]
            if prev_frames:  # Safety check for previous animation
                prev_frame_index = min(self.current_frame, len(prev_frames)-1)
                prev_frame = prev_frames[prev_frame_index]
                blend_factor = self.current_blend / self.animation_blend_time
                self._draw_blended_frames(screen, draw_x, draw_y, 
                                        current_frame, prev_frame, blend_factor)
        else:
            self._draw_frame(screen, draw_x, draw_y, current_frame)

    def _draw_frame(self, screen, x, y, frame):
        """Draw a single frame with safe array access"""
        if not frame:  # Safety check for empty frame
            return
            
        for row_index, row in enumerate(frame):
            for col_index, pixel in enumerate(row):
                if pixel in self.colors and self.colors[pixel]:
                    # Color base
                    base_color = self.colors[pixel]
                    
                    # Añadir brillo dinámico
                    if pixel in ['X', 'A']:
                        glow = int(50 * self.glow_intensity)
                        color = tuple(min(255, c + glow) for c in base_color)
                    else:
                        color = base_color
                    
                    # Aplicar squash y stretch
                    pixel_x = x + col_index * self.pixel_size
                    pixel_y = y + row_index * self.pixel_size * self.squash_stretch
                    
                    # Dibujar píxel
                    pygame.draw.rect(screen, color,
                                  (pixel_x, pixel_y,
                                   self.pixel_size,
                                   self.pixel_size * self.squash_stretch))

    def _draw_blended_frames(self, screen, x, y, current_frame, prev_frame, blend_factor):
        for row_index, (current_row, prev_row) in enumerate(zip(current_frame, prev_frame)):
            for col_index, (current_pixel, prev_pixel) in enumerate(zip(current_row, prev_row)):
                # Obtener colores
                current_color = self.colors.get(current_pixel)
                prev_color = self.colors.get(prev_pixel)
                
                if current_color or prev_color:
                    # Si algún color es None, usar negro para la mezcla
                    current_color = current_color or (0,0,0)
                    prev_color = prev_color or (0,0,0)
                    
                    # Mezclar colores
                    blended_color = tuple(
                        int(prev_color[i] * blend_factor + 
                            current_color[i] * (1 - blend_factor))
                        for i in range(3)
                    )
                    
                    # Aplicar efectos visuales
                    if current_pixel in ['X', 'A'] or prev_pixel in ['X', 'A']:
                        glow = int(50 * self.glow_intensity)
                        blended_color = tuple(min(255, c + glow) 
                                           for c in blended_color)
                    
                    # Dibujar píxel con squash y stretch
                    pixel_x = x + col_index * self.pixel_size
                    pixel_y = y + row_index * self.pixel_size * self.squash_stretch
                    
                    pygame.draw.rect(screen, blended_color,
                                  (pixel_x, pixel_y,
                                   self.pixel_size,
                                   self.pixel_size * self.squash_stretch))

    def set_colors(
        self,
        base_color: Tuple[int, int, int],
        accent_color: Tuple[int, int, int]
    ) -> None:
        """Actualiza los colores del sprite"""
        self.colors['X'] = base_color
        self.colors['A'] = accent_color
        self.parsed_frames_cache.clear()  # Limpiar cache al cambiar colores

    def resize_pixels(self, new_size: int) -> None:
        """Cambia el tamaño de los píxeles del sprite"""
        self.pixel_size = new_size
        self.parsed_frames_cache.clear()  # Limpiar cache al cambiar tamaño