import pygame
from Index.Player.style_player import PlayerStyle
from Index.Utils.collision_helper import CollisionHelper

class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 2000
        self.friction = 0.85
        self.max_velocity = 400
        self.is_jumping = False
        self.is_attacking = False
        self.gravity = 980
        self.jump_power = 500
        self.style = PlayerStyle()
        self.health = 100
        self.on_ground = False

    def move_left(self, dt):
        """Apply left movement force"""
        self.velocity_x -= self.acceleration * dt
        self.velocity_x = max(self.velocity_x, -self.max_velocity)

    def move_right(self, dt):
        """Apply right movement force"""
        self.velocity_x += self.acceleration * dt
        self.velocity_x = min(self.velocity_x, self.max_velocity)

    def jump(self):
        """Make player jump if on ground"""
        if not self.is_jumping and self.on_ground:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.on_ground = False

    def check_platform_collision(self, platforms):
        """Check and handle collisions with platforms"""
        # Crear un rectángulo para el jugador
        player_rect = pygame.Rect(
            self.x,
            self.y,
            self.style.width,
            self.style.height
        )
        
        # Verificar colisiones con todas las plataformas
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                # Si el jugador está cayendo (velocidad_y negativa)
                if self.velocity_y <= 0:
                    # Si el jugador está por encima de la plataforma
                    if self.y + self.style.height <= platform.rect.top + abs(self.velocity_y):
                        self.y = platform.rect.top - self.style.height
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        return True

        # Si no hay colisión con ninguna plataforma
        if self.velocity_y < 0:  # Solo cambiar on_ground si está cayendo
            self.on_ground = False
        return False

    def update(self, dt, platforms=None):
        """Update player state and position"""
        # Aplicar gravedad solo si no está en el suelo
        if not self.on_ground:
            self.velocity_y -= self.gravity * dt

        # Actualizar posición
        self.x += self.velocity_x * dt
        old_y = self.y  # Guardar la posición Y anterior
        self.y += self.velocity_y * dt

        # Verificar colisiones con plataformas
        if platforms:
            self.check_platform_collision(platforms)

        # Aplicar fricción horizontal
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 1:
            self.velocity_x = 0

        # Reset attack state
        if self.is_attacking:
            self.is_attacking = False

    def take_damage(self, amount):
        """Reduce player health by the specified amount"""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        """Draw the player using the style"""
        self.style.draw(screen, self.x, screen.get_height() - self.y - self.style.height)
