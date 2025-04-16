import pygame
import time
import random  # Importar el módulo random
from Index.Enemies.style_enemie import EnemyStyle
from Index.Utils.collision_helper import CollisionHelper

class Enemy:
    # Configuraciones de dificultad
    DIFFICULTY_SETTINGS = {
        0: {  # Fácil
            'health': 80,
            'damage': 8,
            'speed': 200,
            'acceleration': 1200,
            'jump_power': 400,
            'aggro_range': 250,
            'attack_cooldown': 2.0,
            'knockback_resistance': 0.7
        },
        1: {  # Normal
            'health': 100,
            'damage': 10,
            'speed': 300,
            'acceleration': 1500,
            'jump_power': 500,
            'aggro_range': 300,
            'attack_cooldown': 1.5,
            'knockback_resistance': 0.5
        },
        2: {  # Difícil
            'health': 120,
            'damage': 15,
            'speed': 400,
            'acceleration': 1800,
            'jump_power': 600,
            'aggro_range': 400,
            'attack_cooldown': 1.0,
            'knockback_resistance': 0.3
        }
    }

    def __init__(self, x, y, difficulty=1):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.is_jumping = False
        self.attack_range = 60
        self.is_attacking = False
        self.style = EnemyStyle()
        self.last_attack_time = 0
        self.on_ground = False
        self.state = 'patrol'
        self.patrol_direction = 1
        self.patrol_timer = 0
        self.patrol_duration = 2.0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 0.5
        self.friction = 0.85  # Added missing friction attribute
        
        # Aplicar configuración de dificultad
        self.set_difficulty(difficulty)
        
        # Inicializar valores de salud
        self.health = self.max_health
        
    def set_difficulty(self, difficulty):
        """Actualizar parámetros según el nivel de dificultad"""
        settings = self.DIFFICULTY_SETTINGS[difficulty]
        self.max_health = settings['health']
        self.damage = settings['damage']
        self.max_velocity = settings['speed']
        self.acceleration = settings['acceleration']
        self.jump_power = settings['jump_power']
        self.aggro_range = settings['aggro_range']
        self.attack_cooldown = settings['attack_cooldown']
        self.knockback_resistance = settings['knockback_resistance']
        
        # Reiniciar salud al cambiar dificultad
        self.health = self.max_health

    def move_towards_player(self, player, dt):
        """Move towards player with smooth acceleration"""
        # Calcular dirección al jugador
        direction = 1 if player.x > self.x else -1
        target_velocity = self.max_velocity * direction
        
        # Aplicar aceleración
        if abs(self.velocity_x - target_velocity) > self.acceleration * dt:
            self.velocity_x += self.acceleration * direction * dt
        else:
            self.velocity_x = target_velocity
        
        # Limitar velocidad
        self.velocity_x = max(min(self.velocity_x, self.max_velocity), -self.max_velocity)

    def jump(self):
        """Make enemy jump if on ground using screen coordinates"""
        if not self.is_jumping and self.on_ground:
            self.velocity_y = -self.jump_power  # Negativo para saltar hacia arriba
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
        """Check and handle collisions with platforms using screen coordinates"""
        enemy_rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )
        
        for platform in platforms:
            if enemy_rect.colliderect(platform.rect):
                if self.velocity_y >= 0:  # Cayendo (velocidad positiva en coordenadas de pantalla)
                    if self.y <= platform.rect.top:
                        self.y = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        return True

        if self.velocity_y > 0:
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

    def patrol(self, dt):
        """Basic patrol behavior"""
        self.patrol_timer += dt
        if self.patrol_timer >= self.patrol_duration:
            self.patrol_direction *= -1
            self.patrol_timer = 0
        
        self.velocity_x = self.patrol_direction * self.max_velocity * 0.5

    def chase_player(self, player, dt):
        """Enhanced chase behavior with jumping"""
        distance = player.x - self.x
        direction = 1 if distance > 0 else -1
        
        self.velocity_x += self.acceleration * direction * dt
        self.velocity_x = max(min(self.velocity_x, self.max_velocity), -self.max_velocity)
        
        # Jump if player is higher and we're on ground
        if self.on_ground and player.y > self.y + 50:
            self.jump()

    def update(self, player, platforms, dt):
        """Enhanced update with difficulty-based behavior"""
        # Update timers
        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        # Calculate distance to player
        distance_to_player = abs(player.x - self.x)
        
        # State machine with difficulty-based behavior
        if distance_to_player <= self.attack_range:
            self.state = 'attack'
        elif distance_to_player <= self.aggro_range:
            self.state = 'chase'
            # En dificultad difícil, saltar más agresivamente
            if self.max_health >= 120 and self.on_ground and random.random() < 0.05:
                self.jump()
        else:
            self.state = 'patrol'
            
        # Execute current state
        if self.state == 'patrol':
            self.patrol(dt)
        elif self.state == 'chase':
            self.chase_player(player, dt)
        elif self.state == 'attack':
            self.attack(player)
            
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity * dt  # Gravedad positiva para coordenadas de pantalla
            
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Mantener al enemigo dentro de los límites verticales
        screen_height = 450  # Usar la misma altura que el jugador
        if self.y > screen_height - self.height:  # Límite inferior
            self.y = screen_height - self.height
            self.velocity_y = 0
            self.on_ground = True
        elif self.y < 0:  # Límite superior
            self.y = 0
            self.velocity_y = 0
        
        # Check collisions
        self.check_platform_collision(platforms)
        
        # Apply friction
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 1:
            self.velocity_x = 0
            
        # Update animation
        moving = abs(self.velocity_x) > 0.1
        self.style.update_animation(dt, moving=moving, 
                                  jumping=self.is_jumping, 
                                  attacking=self.is_attacking)

    def take_damage(self, amount, knockback_x=0, knockback_y=0):
        """Enhanced damage handling with correct knockback direction"""
        if not self.invulnerable:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            
            # Apply knockback with resistance and correct direction
            self.velocity_x = max(min(knockback_x * (1 - self.knockback_resistance), 300), -300)
            self.velocity_y = -200  # Knockback hacia arriba (negativo en coordenadas de pantalla)
            
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration

    def draw(self, screen):
        """Dibujar al enemigo en la pantalla con coordenadas correctas"""
        self.style.draw(screen, self.x, self.y)
