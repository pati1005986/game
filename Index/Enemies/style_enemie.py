import pygame
import math
import random

class EnemyStyle:
    def __init__(self):
        # Paleta de colores NES mejorada
        self.colors = {
            'X': (201, 0, 0),      # Rojo NES
            'D': (146, 0, 0),      # Rojo oscuro
            'E': (255, 200, 200),  # Rojo claro para ojos
            'B': (0, 0, 0),        # Negro para detalles
            'G': (255, 150, 150),  # Rojo brillante para efectos
            ' ': None              # Transparente
        }
        self.width = 32
        self.height = 32
        self.pixel_size = 8
        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_speeds = {
            'idle': 0.4,
            'run': 0.15,
            'jump': 0.2,
            'attack': 0.1
        }
        self.time_since_last_frame = 0
        self.time_active = 0
        self.glow_intensity = 0
        self.squash_factor = 1.0
        self.shake_offset = 0
        self.particles = []
        
        # Agregar animaciones mejoradas
        self.animations = {
            "idle": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XEXXXXEX ",
                  " XBBXXBBX ",
                  " XXXXXXXX ",
                  "  DDDDDD  ",
                  " XX XX XX ",
                  "XXX    XXX" ],
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XEXXXXEX ",
                  " XBBXXBBX ",
                  " XXXXXXXX ",
                  "  DDDDDD  ",
                  " XXXXXXXX ",
                  " XX DD XX " ]
            ],
            "run": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XEXXXXEX ",
                  " XBBXXBBX ",
                  " XXXXXXXX ",
                  "  DDDDDD  ",
                  " XX  XX   ",
                  "XXX   XX  " ],
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XEXXXXEX ",
                  " XBBXXBBX ",
                  " XXXXXXXX ",
                  "  DDDDDD  ",
                  "   XX  XX ",
                  "  XX   XXX" ]
            ],
            "jump": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XEXXXXEX ",
                  " XBBXXBBX ",
                  " XXXXXXXX ",
                  "  DDDDDD  ",
                  " XXXXXXXX ",
                  "XX    XXX" ]
            ],
            "attack": [
                [ "    XXXX    ",
                  "   XXXXXX   ",
                  "  XEXXXXEX  ",
                  " XXBBXXBBXX ",
                  "XXXXXXXXXX  ",
                  " DDDDDDDD   ",
                  "XXXXXXXX    ",
                  " XX  XXX    " ],
                [ "   XXXX    ",
                  "  XXXXXX   ",
                  " XEXXXXEX  ",
                  "XXBBXXBBX  ",
                  "XXXXXXXX   ",
                  " DDDDDD    ",
                  "XXXXXX     ",
                  "XX  XX     " ]
            ]
        }

    def update_animation(self, dt, moving=False, jumping=False, attacking=False):
        self.time_active += dt
        
        # Actualizar animación actual
        if attacking:
            self.current_animation = "attack"
        elif jumping:
            self.current_animation = "jump"
        else:
            self.current_animation = "run" if moving else "idle"
            
        # Actualizar frame
        frames = self.animations[self.current_animation]
        if len(frames) > 1:
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= self.animation_speeds[self.current_animation]:
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.time_since_last_frame = 0
        else:
            self.current_frame = 0
            
        # Actualizar efectos visuales
        self.glow_intensity = (math.sin(self.time_active * 3) + 1) * 0.5
        
        # Efecto de squash y stretch
        if jumping:
            self.squash_factor = 1.2
        elif moving:
            self.squash_factor = 1.0 + math.sin(self.time_active * 10) * 0.1
        else:
            self.squash_factor = 1.0 + math.sin(self.time_active * 2) * 0.05
            
        # Efecto de vibración al atacar
        if attacking:
            self.shake_offset = random.randint(-2, 2)
        else:
            self.shake_offset = 0
            
        # Actualizar partículas
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
                
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            
        # Generar nuevas partículas durante el ataque
        if attacking and random.random() < 0.3:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': 0,
                'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.uniform(0.2, 0.5),
                'max_lifetime': 0.5,
                'alpha': 255
            })

    def draw(self, screen, x, y):
        # Aplicar transformaciones
        draw_x = x + self.shake_offset
        draw_y = y
        scaled_height = self.height * self.squash_factor
        height_diff = scaled_height - self.height
        draw_y -= height_diff
        
        # Dibujar partículas
        for particle in self.particles:
            color = (*self.colors['G'][:3], particle['alpha'])
            pos = (int(draw_x + particle['x']), int(draw_y + particle['y']))
            pygame.draw.circle(screen, color, pos, 2)
        
        # Dibujar sprite principal con efectos
        frames = self.animations[self.current_animation]
        frame = frames[self.current_frame]
        
        for row_index, row in enumerate(frame):
            for col_index, pixel in enumerate(row):
                if pixel in self.colors and self.colors[pixel]:
                    # Aplicar color base
                    base_color = self.colors[pixel]
                    
                    # Añadir brillo dinámico
                    if pixel in ['X', 'D']:
                        glow = int(50 * self.glow_intensity)
                        color = tuple(min(255, c + glow) for c in base_color)
                    else:
                        color = base_color
                    
                    # Calcular posición con squash y stretch
                    pixel_x = draw_x + col_index * self.pixel_size
                    pixel_y = draw_y + row_index * self.pixel_size * self.squash_factor
                    
                    # Dibujar píxel
                    pygame.draw.rect(screen, color,
                                  (pixel_x, pixel_y,
                                   self.pixel_size,
                                   self.pixel_size * self.squash_factor))
