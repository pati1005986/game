import pygame
import time
from Index.Enemies.style_enemie import EnemyStyle

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity_x = 2  # Velocidad de movimiento horizontal
        self.velocity_y = 0  # Velocidad de movimiento vertical
        self.gravity = 1
        self.is_jumping = False
        self.jump_power = -10
        self.attack_range = 10  # Rango de ataque
        self.is_attacking = False
        self.damage = 10  # Daño infligido al jugador
        self.style = EnemyStyle()  # Inicializar estilo del enemigo
        self.attack_cooldown = 1.0  # Tiempo de recarga entre ataques en segundos
        self.last_attack_time = 0  # Tiempo del último ataque

    def move_towards_player(self, player):
        """Moverse hacia el jugador"""
        if self.x < player.x:
            self.x += self.velocity_x
        elif self.x > player.x:
            self.x -= self.velocity_x

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

    def update(self, player, platforms):
        """Actualizar estado y posición del enemigo"""
        self.move_towards_player(player)
        self.attack(player)

        # Aplicar gravedad
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Check for collisions with platforms
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        on_ground = False
        for platform in platforms:
            if enemy_rect.colliderect(platform.rect) and self.velocity_y > 0:
                self.y = platform.rect.top - self.height
                self.velocity_y = 0
                self.is_jumping = False
                on_ground = True
                break

        if not on_ground and self.y < 0:
            self.is_jumping = True

        # Actualizar animación
        self.style.update_animation(0, moving=True, jumping=self.is_jumping, attacking=self.is_attacking)

    def draw(self, screen):
        """Dibujar al enemigo en la pantalla"""
        self.style.draw(screen, self.x, screen.get_height() - self.y - self.height)
