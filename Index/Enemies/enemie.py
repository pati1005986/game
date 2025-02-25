import pygame
import random
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
        self.attack_range = 100  # Rango de ataque
        self.is_attacking = False               
        self.damage = 10  # Daño infligido al jugador
        self.style = EnemyStyle()  # Inicializar estilo del enemigo

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
        """Iniciar ataque si el jugador está en rango"""
        distance = abs(self.x - player.x)
        if distance <= self.attack_range:
            self.is_attacking = True
            player.take_damage(self.damage)  # Infligir daño al jugador
        else:
            self.is_attacking = False

    def update(self, player):
        """Actualizar estado y posición del enemigo"""
        self.move_towards_player(player)
        self.attack(player)

        # Aplicar gravedad
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        # Resetear salto cuando el enemigo aterriza
        if self.y >= 0:  # Suponiendo que el nivel del suelo es y=0
            self.y = 0
            self.velocity_y = 0
            self.is_jumping = False

        # Actualizar animación
        self.style.update_animation(0, moving=True, jumping=self.is_jumping, attacking=self.is_attacking)

    def draw(self, screen):
        """Dibujar al enemigo en la pantalla"""
        self.style.draw(screen, self.x, screen.get_height() - self.y - self.height)
