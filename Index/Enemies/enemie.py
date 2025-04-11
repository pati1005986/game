import pygame
import time
import random  # Importar el módulo random
from Index.Enemies.style_enemie import EnemyStyle

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.base_velocity = 200  # Units per second
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.is_jumping = False
        self.jump_power = 500
        self.attack_range = 50
        self.is_attacking = False
        self.damage = 10
        self.style = EnemyStyle()
        self.attack_cooldown = 1.0
        self.last_attack_time = 0

    def move_towards_player(self, player, dt):
        if self.x < player.x:
            self.velocity_x = self.base_velocity
        elif self.x > player.x:
            self.velocity_x = -self.base_velocity
        else:
            self.velocity_x = 0

    def jump(self):
        """Hacer que el enemigo salte"""
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def attack(self, player):
        """Iniciar ataque si el jugador está en rango y el cooldown ha pasado"""
        current_time = time.time()
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.style.width, player.style.height)
        if enemy_rect.colliderect(player_rect) and current_time - self.last_attack_time >= self.attack_cooldown:
            self.is_attacking = True
            player.take_damage(self.damage)  # Infligir daño al jugador
            self.last_attack_time = current_time  # Actualizar tiempo del último ataque
        else:
            self.is_attacking = False

    def update(self, player, platforms, dt):
        self.move_towards_player(player, dt)
        self.attack(player)

        # Apply gravity
        self.velocity_y -= self.gravity * dt
        
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Handle platform collisions
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        on_ground = False
        for platform in platforms:
            if enemy_rect.colliderect(platform.rect) and self.velocity_y < 0:
                self.y = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False
                on_ground = True
                break

        # Random jumping when on ground
        if on_ground and not self.is_jumping and random.random() < 0.01:
            self.jump()

        # Reset horizontal velocity
        self.velocity_x = 0

        # Actualizar animación
        self.style.update_animation(dt, moving=abs(self.velocity_x) > 0, jumping=self.is_jumping, attacking=self.is_attacking)

    def draw(self, screen):
        """Dibujar al enemigo en la pantalla"""
        self.style.draw(screen, self.x, screen.get_height() - self.y - self.height)
