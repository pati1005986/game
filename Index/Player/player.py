import pygame
from Index.Player.style_player import PlayerStyle
from Index.Utils.collision_helper import CollisionHelper

class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 3000  # Increased for snappier movement
        self.friction = 0.82  # Adjusted for better control
        self.max_velocity = 500  # Increased max speed
        self.is_jumping = False
        self.is_attacking = False
        self.gravity = 1500  # Increased gravity
        self.jump_power = 650  # Increased jump power
        self.style = PlayerStyle()
        self.health = 100
        self.on_ground = False
        self.double_jump_available = True  # New double jump mechanic
        self.coyote_time = 0.1  # Time window to jump after leaving platform
        self.coyote_timer = 0
        self.dash_power = 1000  # New dash ability
        self.dash_cooldown = 0.5
        self.dash_timer = 0
        self.dash_available = True
        self.facing_right = True  # Track player direction
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 1.0
        self.screen_height = 450  # Añadir referencia a la altura de la pantalla

    def move_left(self, dt):
        """Apply left movement force"""
        self.velocity_x -= self.acceleration * dt
        self.velocity_x = max(self.velocity_x, -self.max_velocity)
        self.facing_right = False

    def move_right(self, dt):
        """Apply right movement force"""
        self.velocity_x += self.acceleration * dt
        self.velocity_x = min(self.velocity_x, self.max_velocity)
        self.facing_right = True

    def jump(self):
        """Jump with correct direction in screen coordinates"""
        if self.on_ground or self.coyote_timer > 0:
            self.velocity_y = -self.jump_power  # Negativo para saltar hacia arriba
            self.is_jumping = True
            self.on_ground = False
            self.double_jump_available = True
            self.coyote_timer = 0
        elif self.double_jump_available and not self.on_ground:
            self.velocity_y = -self.jump_power * 0.8  # Negativo para saltar hacia arriba
            self.double_jump_available = False

    def dash(self, dt):
        """New dash ability"""
        if self.dash_available:
            direction = 1 if self.facing_right else -1
            self.velocity_x = self.dash_power * direction
            self.dash_available = False
            self.dash_timer = self.dash_cooldown
            self.invulnerable = True
            self.invulnerable_timer = 0.2

    def attack(self):
        """Initiate player attack"""
        self.is_attacking = True

    def check_platform_collision(self, platforms):
        """Check and handle collisions with platforms using screen coordinates"""
        player_rect = pygame.Rect(
            self.x,
            self.y,
            self.style.width,
            self.style.height
        )
        
        for platform in platforms:
            if player_rect.colliderect(platform.rect):
                if self.velocity_y >= 0:  # Cayendo (velocidad positiva en coordenadas de pantalla)
                    if self.y <= platform.rect.top:
                        self.y = platform.rect.top
                        self.velocity_y = 0
                        self.is_jumping = False
                        self.on_ground = True
                        return True

        if self.velocity_y > 0:  # Si está cayendo en coordenadas de pantalla
            self.on_ground = False
        return False

    def update(self, dt, platforms=None):
        """Optimized update method with modularized logic."""
        self.update_timers(dt)
        self.apply_physics(dt)
        self.handle_collisions(platforms)
        self.constrain_to_screen()
        self.update_animation(dt)
        self.reset_attack_state()

    def update_timers(self, dt):
        """Update timers for dash, invulnerability, and coyote time."""
        if not self.dash_available:
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_available = True

        if self.invulnerable:
            self.invulnerable_timer -= dt
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        if not self.on_ground:
            self.coyote_timer -= dt
        else:
            self.coyote_timer = self.coyote_time

    def apply_physics(self, dt):
        """Apply gravity and update position."""
        if not self.on_ground:
            self.velocity_y += self.gravity * dt

        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

        # Apply friction
        self.velocity_x *= self.friction
        if abs(self.velocity_x) < 1:
            self.velocity_x = 0

    def handle_collisions(self, platforms):
        """Handle collisions with platforms."""
        if platforms:
            self.check_platform_collision(platforms)

    def constrain_to_screen(self):
        """Ensure the player stays within screen bounds."""
        if self.y > self.screen_height - self.style.height:
            self.y = self.screen_height - self.style.height
            self.velocity_y = 0
            self.on_ground = True
        elif self.y < 0:
            self.y = 0
            self.velocity_y = 0

    def update_animation(self, dt):
        """Update player animation based on state."""
        is_moving = abs(self.velocity_x) > 1
        self.style.update_animation(dt, moving=is_moving, jumping=self.is_jumping, attacking=self.is_attacking)

    def reset_attack_state(self):
        """Reset the attack state after each update."""
        if self.is_attacking:
            self.is_attacking = False

    def take_damage(self, amount):
        """Damage handling with correct knockback direction"""
        if not self.invulnerable:
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            
            # Knockback hacia arriba (valor negativo en coordenadas de pantalla)
            self.velocity_y = -300  # Knockback vertical
            knockback_x = 200 if self.facing_right else -200
            self.velocity_x = knockback_x

    def draw(self, screen):
        """Draw the player on screen with correct coordinates"""
        self.style.draw(screen, self.x, self.y)
