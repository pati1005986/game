import pygame
import time
import random  # Importar el módulo random
from Index.Enemies.style_enemie import EnemyStyle
from Index.Utils.collision_helper import CollisionHelper

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 1500
        self.friction = 0.85
        self.max_velocity = 300
        self.gravity = 980
        self.jump_power = 500
        self.is_jumping = False
        self.attack_range = 50
        self.is_attacking = False
        self.damage = 10
        self.style = EnemyStyle()
        self.attack_cooldown = 1.0
        self.last_attack_time = 0
        self.on_ground = False

    def move_towards_player(self, player, dt):
        """Move towards player with smooth acceleration"""
        if self.x < player.x:
            self.velocity_x += self.acceleration * dt
        else:
            self.velocity_x -= self.acceleration * dt
        
        # Clamp velocity
        self.velocity_x = max(min(self.velocity_x, self.max_velocity), -self.max_velocity)

    def jump(self):
        """Make enemy jump if on ground"""
        if not self.is_jumping and self.on_ground:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.on_ground = False

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

    def check_platform_collision(self, platforms):
        """Check and handle collisions with platforms"""
        enemy_rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )
        
        for platform in platforms:
            if enemy_rect.colliderect(platform.rect):
                if self.velocity_y <= 0:
                    if self.y + self.height <= platform.rect.top + abs(self.velocity_y):
                        self.y = platform.rect.top - self.height
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        return True

        if self.velocity_y < 0:
            self.on_ground = False
        return False

    def check_player_collision(self, player):
        """Check for collision with player and handle attack"""
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.style.width, player.style.height)
        
        if enemy_rect.colliderect(player_rect):
            current_time = time.time()
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.is_attacking = True
                player.take_damage(self.damage)
                self.last_attack_time = current_time
                return True
        return False

    def update(self, player, platforms, dt):
        """Update enemy state and position"""
        self.move_towards_player(player, dt)
        
        # Aplicar gravedad solo si no está en el suelo
        if not self.on_ground:
            self.velocity_y -= self.gravity * dt

        # Actualizar posición
        self.x += self.velocity_x * dt
        old_y = self.y
        self.y += self.velocity_y * dt

        # Verificar colisiones
        self.check_platform_collision(platforms)

        # Apply friction
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 1:
            self.velocity_x = 0

        # Random jumping when near player and on ground
        if self.on_ground and abs(self.x - player.x) < 200 and random.random() < 0.02:
            self.jump()

        # Attack check
        self.attack(player)

        # Update animation
        self.style.update_animation(dt, moving=abs(self.velocity_x) > 0.1, 
                                  jumping=self.is_jumping, 
                                  attacking=self.is_attacking)

    def draw(self, screen):
        """Dibujar al enemigo en la pantalla"""
        self.style.draw(screen, self.x, screen.get_height() - self.y)
