import pygame

class EnemyStyle:
    def __init__(self):
        self.color = (200, 0, 0)  # Rojo más oscuro para el enemigo
        self.width = 60           # Ancho aumentado
        self.height = 60          # Alto aumentado
        self.animations = {
            "idle": [
                [ "  XXXX  ",
                  " XXXXXX ",
                  "XXXXXXXX",
                  "XX XX XX",
                  "XXXXXXXX",
                  " XXXXXX ",
                  "  XXXX  " ]
            ],
            "run": [
                [ " XXXX   ",
                  "XXXXXX  ",
                  "XXXXXXX ",
                  "XX XX XX",
                  "XXXXXXX ",
                  " XXXXX  ",
                  "  XXX   " ],
                [ "   XXXX ",
                  "  XXXXXX",
                  " XXXXXXX",
                  "XX XX XX",
                  " XXXXXXX",
                  "  XXXXX ",
                  "   XXX  " ]
            ],
            "jump": [
                [ "   XX   ",
                  "  XXXX  ",
                  " XXXXXX ",
                  "XXXXXXXX",
                  " XX  XX ",
                  "  XXXX  " ]
            ],
            "attack": [
                [ " AXXXA  ",
                  "AXXXXXA ",
                  "XXXXXXXX",
                  "XXXXXXXX",
                  "AXXXXXA ",
                  " AXXXA  " ],
                [ "  AXXA  ",
                  " AXXXA  ",
                  "XXXXXXXX",
                  "XXXXXXXX",
                  " AXXXA  ",
                  "  AXXA  " ]
            ]
        }
        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_speed = 0.15  # segundos por frame
        self.time_since_last_frame = 0

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
            if self.time_since_last_frame >= self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.time_since_last_frame = 0
        else:
            self.current_frame = 0

    def draw_pixel_art(self, screen, x, y):
        """Dibuja el frame actual de la animación en pixel art"""
        frames = self.animations[self.current_animation]
        frame = frames[self.current_frame]
        for row_index, row in enumerate(frame):
            for col_index, pixel in enumerate(row):
                if pixel in ('X', 'A'):
                    pygame.draw.rect(screen, self.color, (x + col_index * 10, y + row_index * 10, 10, 10))

    def draw(self, screen, x, y):
        """Dibuja el enemigo usando la animación en pixel art"""
        self.draw_pixel_art(screen, x, y)
