import pygame
from Index.Player.style_player import PlayerStyle

class Player:
    def __init__(self, x=0, y=0):
        self.x = x  # X position
        self.y = y  # Y position
        self.velocity_x = 5  # Horizontal movement speed
        self.velocity_y = 0  # Vertical movement speed
        self.is_jumping = False
        self.is_attacking = False
        self.gravity = 1
        self.jump_power = -15
        self.style = PlayerStyle()  # Initialize player style
        self.health = 100  # Health of the player

    def move_left(self):
        """Move player to the left"""
        self.x -= self.velocity_x

    def move_right(self):
        """Move player to the right"""
        self.x += self.velocity_x

    def jump(self):
        """Make player jump if not already jumping"""
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def attack(self):
        """Initiate player attack"""
        self.is_attacking = True
        # Attack duration could be handled in update method

    def update(self):
        """Update player state and position"""
        # Apply gravity
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        
        # Eliminar o ajustar esta condición para que no reinicie siempre el salto:
        # if self.y >= 0:
        #     self.y = 0
        #     self.velocity_y = 0
        #     self.is_jumping = False
            
        # Reset attack after duration
        if self.is_attacking:
            # Attack duration logic here
            self.is_attacking = False

    def take_damage(self, amount):
        """Reduce player health by the specified amount"""
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def draw(self, screen):
        """Draw the player using the style"""
        self.style.draw(screen, self.x, screen.get_height() - self.y - self.style.height)
