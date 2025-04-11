import pygame
from Index.Player.style_player import PlayerStyle

class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.base_velocity = 300  # Units per second
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_jumping = False
        self.is_attacking = False
        self.gravity = 980  # Pixels per second squared
        self.jump_power = 500
        self.style = PlayerStyle()
        self.health = 100

    def move_left(self):
        self.velocity_x = -self.base_velocity

    def move_right(self):
        self.velocity_x = self.base_velocity

    def jump(self):
        """Make player jump if not already jumping"""
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def attack(self):
        """Initiate player attack"""
        self.is_attacking = True
        # Attack duration could be handled in update method

    def update(self, dt, platforms=None):
        """Update player state and position"""
        # Apply gravity
        self.velocity_y -= self.gravity * dt
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Handle platform collisions
        if platforms:
            player_rect = pygame.Rect(self.x, self.y, self.style.width, self.style.height)
            for platform in platforms:
                if player_rect.colliderect(platform.rect) and self.velocity_y < 0:
                    self.y = platform.rect.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    break

        # Reset attack after duration
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
