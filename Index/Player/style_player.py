import pygame
from typing import Dict, List, Tuple

class PlayerStyle:
    def __init__(
        self,
        base_color: Tuple[int, int, int] = (34, 177, 76),  # Verde claro como Link
        accent_color: Tuple[int, int, int] = (181, 230, 29),  # Verde más claro para detalles
        pixel_size: int = 8  # Píxeles más grandes para estilo NES
    ):
        self.colors = {
            'X': base_color,        # Color base del personaje
            'A': accent_color,      # Detalles del personaje
            'B': (139, 69, 19),    # Marrón para detalles
            'W': (255, 255, 255),   # Blanco para efectos
            ' ': None              # Transparente
        }
        
        self.pixel_size = pixel_size
        self.width = 32  # Tamaño más pequeño, estilo NES
        self.height = 32
        
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
            'idle': 0.5,    # Más lento para idle
            'run': 0.15,    # Más rápido para correr
            'jump': 0.2,
            'attack': 0.1
        }
        
        self.current_animation = 'idle'
        self.current_frame = 0
        self.time_since_last_frame = 0
        self.parsed_frames_cache = {}

    def update_animation(
        self,
        dt: float,
        moving: bool = False,
        jumping: bool = False,
        attacking: bool = False,
        allow_interrupt: bool = True
    ) -> None:
        """Actualiza la animación con lógica mejorada"""
        new_animation = self._determine_animation_state(moving, jumping, attacking)
        
        if new_animation != self.current_animation:
            if allow_interrupt or self._is_animation_complete():
                self._change_animation(new_animation)

        self._update_frame_progress(dt)

    def _determine_animation_state(
        self,
        moving: bool,
        jumping: bool,
        attacking: bool
    ) -> str:
        """Determina el estado de animación apropiado"""
        if attacking:
            return 'attack'
        if jumping:
            return 'jump'
        return 'run' if moving else 'idle'

    def _change_animation(self, new_animation: str) -> None:
        """Cambia a una nueva animación con reset de frame"""
        if new_animation not in self.animations:
            raise ValueError(f"Animación no válida: {new_animation}")
        
        self.previous_animation = self.current_animation
        self.current_animation = new_animation
        self.current_frame = 0
        self.time_since_last_frame = 0

    def _update_frame_progress(self, dt: float) -> None:
        """Actualiza el progreso de los frames de animación"""
        frames = self.animations[self.current_animation]
        animation_speed = self.animation_speeds[self.current_animation]
        
        if len(frames) > 1:
            self.time_since_last_frame += dt
            if self.time_since_last_frame >= animation_speed:
                self.current_frame = (self.current_frame + 1) % len(frames)
                self.time_since_last_frame = 0

    def _is_animation_complete(self) -> bool:
        """Verifica si la animación actual ha completado un ciclo"""
        return self.current_frame == len(self.animations[self.current_animation]) - 1

    def _parse_animation_frame(self, frame: List[str]) -> List[pygame.Rect]:
        """Parsea un frame de animación a rectángulos optimizados"""
        parsed = []
        for y, row in enumerate(frame):
            for x, pixel in enumerate(row):
                if pixel in self.colors and self.colors[pixel]:
                    rect = pygame.Rect(
                        x * self.pixel_size,
                        y * self.pixel_size,
                        self.pixel_size,
                        self.pixel_size
                    )
                    parsed.append((rect, self.colors[pixel]))
        return parsed

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        """Dibuja el player con optimizaciones de rendimiento"""
        frame_key = f"{self.current_animation}_{self.current_frame}"
        
        if frame_key not in self.parsed_frames_cache:
            frame_data = self.animations[self.current_animation][self.current_frame]
            self.parsed_frames_cache[frame_key] = self._parse_animation_frame(frame_data)
        
        for rect, color in self.parsed_frames_cache[frame_key]:
            screen_rect = rect.move(x, y)
            pygame.draw.rect(screen, color, screen_rect)

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