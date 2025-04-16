import pygame

class EnemyStyle:
    def __init__(self):
        self.colors = {
            'X': (220, 20, 60),  # Rojo carmesí
            'A': (255, 69, 0),   # Rojo-naranja para efectos
            ' ': None  # Transparente
        }
        self.width = 60
        self.height = 60
        self.pixel_size = 8
        self.current_animation = "idle"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.time_since_last_frame = 0
        self.animations = {
            "idle": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXXXXXXX ",
                  "XXX XX XXX",
                  "XXXXXXXXXX",
                  "XXXXXXXXXX",
                  " XXXXXXXX ",
                  "  XX  XX  ",
                  " XXX  XXX " ]
            ],
            "run": [
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXXXXXXX ",
                  "XXX XX XXX",
                  "XXXXXXXXXX",
                  "XXXXXXXXXX",
                  "  XXXXXX  ",
                  " XXX  XX  ",
                  "XXX    X  " ],
                [ "   XXXX   ",
                  "  XXXXXX  ",
                  " XXXXXXXX ",
                  "XXX XX XXX",
                  "XXXXXXXXXX",
                  "XXXXXXXXXX",
                  "  XXXXXX  ",
                  "  XX  XXX ",
                  "  X    XXX" ]
            ],
            "jump": [
                [ "   XXXX   ",
                  " XXXXXXXX ",
                  "XXXXXXXXXX",
                  "XXX XX XXX",
                  " XXXXXXXX ",
                  "  XXXXXX  ",
                  " XXXXXXXX ",
                  "XX      XX",
                  " XXX  XXX " ]
            ],
            "attack": [
                [ "    AAAA   ",
                  "   AAAAAA  ",
                  "  AAAAAAAA ",
                  " AXXXXXXXA ",
                  "AXXXXXXXXXA",
                  " AXXXXXXXA ",
                  "  AAAAAAAA ",
                  "   AAAAAA  ",
                  "    AAAA   " ],
                [ "   AAAA    ",
                  "  AAAAAA   ",
                  " AAAAAAAA  ",
                  " AXXXXXXXA ",
                  "AXXXXXXXXXA",
                  " AXXXXXXXA ",
                  " AAAAAAAA  ",
                  "  AAAAAA   ",
                  "   AAAA    " ]
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
            if self.time_since_last_frame >= self.animation_speed:
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
