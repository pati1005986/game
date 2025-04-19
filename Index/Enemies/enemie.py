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
        self.style = EnemyStyle()
        self.width = self.style.width  # Usar el ancho del sprite
        self.height = self.style.height  # Usar el alto del sprite
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 980
        self.is_jumping = False
        self.attack_range = 60
        self.is_attacking = False
        self.last_attack_time = 0
        self.on_ground = False
        self.state = 'patrol'
        self.patrol_direction = 1
        self.patrol_timer = 0
        self.patrol_duration = 2.0
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 0.5
        self.friction = 0.85
        
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
        # Crear rect del enemigo con las dimensiones correctas del sprite
        enemy_rect = pygame.Rect(
            self.x,
            self.y,
            self.width,
            self.height
        )
        
        # Variable para rastrear si estamos en el suelo
        was_on_ground = self.on_ground
        self.on_ground = False
        
        for platform in platforms:
            if enemy_rect.colliderect(platform.rect):
                # Obtener la profundidad de la colisión en cada eje
                dx = min(enemy_rect.right - platform.rect.left, platform.rect.right - enemy_rect.left)
                dy = min(enemy_rect.bottom - platform.rect.top, platform.rect.bottom - enemy_rect.top)
                
                # Determinar la dirección de la colisión comparando las profundidades
                if dx < dy:  # Colisión horizontal
                    if enemy_rect.centerx < platform.rect.centerx:  # Colisión desde la izquierda
                        self.x = platform.rect.left - self.width
                    else:  # Colisión desde la derecha
                        self.x = platform.rect.right
                    self.velocity_x = 0
                else:  # Colisión vertical
                    if enemy_rect.centery < platform.rect.centery:  # Colisión desde arriba
                        self.y = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                    else:  # Colisión desde abajo
                        self.y = platform.rect.bottom
                        self.velocity_y = 0
                
        # Si acabamos de dejar el suelo, aplicar un pequeño impulso hacia arriba
        if was_on_ground and not self.on_ground and self.velocity_y >= 0:
            self.velocity_y = -100  # Pequeño impulso para hacer el movimiento más suave
            
        return self.on_ground

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
        """Enhanced chase behavior with jumping and smarter movement"""
        distance_x = player.x - self.x
        distance_y = player.y - self.y
        direction = 1 if distance_x > 0 else -1
        
        # Actualizar dirección del movimiento
        self.velocity_x += self.acceleration * direction * dt
        self.velocity_x = max(min(self.velocity_x, self.max_velocity), -self.max_velocity)
        
        # Ajustar agresividad basada en la salud del enemigo
        aggression = 1.0 + (1.0 - self.health / self.max_health)
        
        # Saltar si:
        # 1. El jugador está más alto
        # 2. Hay una plataforma arriba
        # 3. Estamos en el suelo
        if self.on_ground and (
            (distance_y < -50) or  # Jugador está más alto
            (abs(distance_x) < self.attack_range and random.random() < 0.1 * aggression)  # Salto agresivo
        ):
            self.jump()
        
        # Intentar atacar si está en rango
        if abs(distance_x) < self.attack_range and abs(distance_y) < 50:
            self.attack(player)

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
            self.velocity_y += self.gravity * dt
            
        # Update position
        prev_x = self.x
        prev_y = self.y
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Check collisions with platforms and resolve them
        collision_found = False
        for platform in platforms:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(platform.rect):
                # Restaurar posición anterior y resolver colisión
                self.x = prev_x
                self.y = prev_y
                
                # Verificar colisión vertical
                if self.velocity_y >= 0:  # Cayendo
                    if self.y <= platform.rect.top:
                        self.y = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        collision_found = True
                elif self.velocity_y < 0:  # Subiendo
                    if self.y + self.height >= platform.rect.bottom:
                        self.y = platform.rect.bottom
                        self.velocity_y = 0
                
                # Verificar colisión horizontal
                if not collision_found:  # Solo si no hubo colisión vertical
                    if self.velocity_x > 0:  # Moviendo a la derecha
                        self.x = platform.rect.left - self.width
                        self.velocity_x = 0
                    elif self.velocity_x < 0:  # Moviendo a la izquierda
                        self.x = platform.rect.right
                        self.velocity_x = 0
        
        if not collision_found:
            self.on_ground = False
        
        # Mantener al enemigo dentro de los límites de la pantalla
        screen_height = 450
        if self.y > screen_height - self.height:
            self.y = screen_height - self.height
            self.velocity_y = 0
            self.on_ground = True
        elif self.y < 0:
            self.y = 0
            self.velocity_y = 0
        
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
