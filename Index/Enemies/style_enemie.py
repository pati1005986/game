import pygame

class EnemyStyle:
    def __init__(self):
        # Paleta de colores NES
        self.colors = {
            'X': (201, 0, 0),      # Rojo NES
            'D': (146, 0, 0),      # Rojo oscuro
            'E': (255, 200, 200),  # Rojo claro para ojos
            'B': (0, 0, 0),        # Negro para detalles
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
        """
        Actualiza el frame de la animación:
        - Si attacking es True se usa "attack".
        - Si no y jumping es True se usa "jump".
        - Si no, si moving es True se usa "run", sino "idle".
        """
        if attacking:
            self.current_animation = "attack"
        elif jumping:
            self.current_animation = "jump"
        else:
            self.current_animation = "run" if moving else "idle"

        frames = self.animations[self.current_animation]
        if len(frames) > 1:
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= self.animation_speeds[self.current_animation]:
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.time_since_last_frame = 0
        else:
            self.current_frame = 0

    def draw_pixel_art(self, screen, x, y):
        """Dibuja el frame actual de la animación en pixel art con colores específicos"""
        frames = self.animations[self.current_animation]
        frame = frames[self.current_frame]
        for row_index, row in enumerate(frame):
            for col_index, pixel in enumerate(row):
                if pixel in self.colors and self.colors[pixel]:
                    color = self.colors[pixel]
                    pygame.draw.rect(screen, color, 
                                  (x + col_index * self.pixel_size, 
                                   y + row_index * self.pixel_size, 
                                   self.pixel_size, self.pixel_size))

    def draw(self, screen, x, y):
        """Dibuja el enemigo usando la animación en pixel art"""
        self.draw_pixel_art(screen, x, y)
