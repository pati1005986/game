import pygame
import sys
import os
import random

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Index.Player.player import Player
from Index.World.style_worlds import draw_gradient_background  # Importa el fondo con gradiente
from Index.World.procedural_levels import generate_platforms  # Nueva generación procedural de plataformas
from Index.Enemies.enemie import Enemy

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particle(self, x, y, color, velocity_x, velocity_y, lifetime=1.0):
        self.particles.append({
            'x': x, 'y': y,
            'vx': velocity_x, 'vy': velocity_y,
            'color': color,
            'lifetime': lifetime,
            'size': 5
        })
    
    def update(self, dt):
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] -= 500 * dt  # Gravity
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime']))
            color = (*particle['color'], alpha)
            surf = pygame.Surface((particle['size'], particle['size']), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (particle['size']//2, particle['size']//2), particle['size']//2)
            screen.blit(surf, (particle['x'], screen.get_height() - particle['y']))

# Initialize systems
particles = ParticleSystem()
score = 0
combo = 0
combo_timer = 0
max_combo = 0

def create_damage_particles(x, y, amount):
    for _ in range(5):
        vx = random.uniform(-100, 100)
        vy = random.uniform(100, 200)
        particles.add_particle(x, y, RED, vx, vy, 0.5)

def show_floating_text(screen, text, x, y, color, size=20):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x - text_surface.get_width()//2, 
                              screen.get_height() - y))

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Level 1")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Variables de nivel
current_level = 1

# Initialize platforms first
platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)

# Create player and enemy instances and position them on the platform
player_x = 100
player_y = platforms[0].rect.top  # Ahora directamente sobre la plataforma
enemy_x = SCREEN_WIDTH - 200
enemy_y = platforms[0].rect.top   # Enemigo también sobre la plataforma

player = Player(x=player_x, y=player_y)
enemy = Enemy(x=enemy_x, y=enemy_y)

def show_game_over(screen, victory=False):
    """Mostrar pantalla de Game Over con mensaje personalizado"""
    font = pygame.font.SysFont(None, 72)
    if victory:
        text = 'Victoria!'
        color = (0, 255, 0)  # Verde para victoria
    else:
        text = 'Game Over'
        color = (255, 0, 0)  # Rojo para derrota
    
    game_over_text = font.render(text, True, color)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

def check_entity_fall(entity, screen_height):
    """Check if an entity has fallen off screen"""
    return entity.y < -screen_height

def reset_level(current_level, screen_width, screen_height):
    """Reset level and return new platforms and positions"""
    platforms = generate_platforms(current_level, screen_width, screen_height)
    player_x, player_y = platforms[0].get_spawn_position()
    enemy_x = screen_width - 100  # Position enemy on the right side
    enemy_y = platforms[0].get_spawn_position()[1]  # Same height as player
    return platforms, (player_x, player_y), (enemy_x, enemy_y)

def update_entities(player, enemy, platforms, dt):
    """Update all entities with collision checks"""
    # Update entities
    player.update(dt, platforms)
    enemy.update(player, platforms, dt)

    # Check entity collisions
    if enemy.check_player_collision(player):
        # Collision response is handled inside check_player_collision
        pass

    # Check for falls
    if check_entity_fall(player, SCREEN_HEIGHT):
        return True, False  # Player fell, next level
    elif check_entity_fall(enemy, SCREEN_HEIGHT):
        return False, True  # Enemy fell, victory

    return False, False  # Continue current level

def check_platform_collisions(entity, platforms):
    """Unified platform collision checking"""
    entity_rect = pygame.Rect(
        entity.x,
        screen.get_height() - entity.y - entity.style.height,  # Convert to screen coordinates
        entity.style.width,
        entity.style.height
    )
    
    for platform in platforms:
        if entity_rect.colliderect(platform.rect):
            # Get collision depth
            dx = min(entity_rect.right - platform.rect.left, platform.rect.right - entity_rect.left)
            dy = min(entity_rect.bottom - platform.rect.top, platform.rect.bottom - entity_rect.top)

            # Determine collision side by comparing depths
            if dx < dy:
                if entity_rect.centerx < platform.rect.centerx:
                    entity.x = platform.rect.left - entity.style.width
                else:
                    entity.x = platform.rect.right
                entity.velocity_x = 0
            else:
                if entity_rect.centery < platform.rect.centery:
                    entity.y = screen.get_height() - platform.rect.top - entity.style.height
                    entity.velocity_y = 0
                    entity.is_jumping = False
                    return True  # On ground
                else:
                    entity.y = screen.get_height() - platform.rect.bottom
                    entity.velocity_y = 0
    return False

def check_level_transition(player, screen_width):
    """Check if player has exited the screen horizontally"""
    if player.x < -50:  # Left exit
        return True, "left"
    elif player.x > screen_width + 50:  # Right exit
        return True, "right"
    return False, None

def reset_player_position(player, direction, screen_width):
    """Reset player position based on exit direction"""
    if direction == "left":
        player.x = screen_width - 200
    else:  # right
        player.x = 100
    player.y = platforms[0].rect.top  # Posición directa sobre la plataforma
    player.velocity_y = 0  # Resetear velocidad vertical

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()
            elif event.key == pygame.K_LSHIFT:  # New dash mechanic
                player.dash(dt)

    # Handle key presses and animations
    keys = pygame.key.get_pressed()
    moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
    player.style.update_animation(dt, moving, player.is_jumping, player.is_attacking)
    
    if keys[pygame.K_LEFT]:
        player.move_left(dt)
    if keys[pygame.K_RIGHT]:
        player.move_right(dt)
    if keys[pygame.K_a]:  # Attack
        player.attack()
        # Check if attack hits enemy
        if abs(player.x - enemy.x) < 60 and abs(player.y - enemy.y) < 60:
            knockback_x = 500 if player.facing_right else -500
            enemy.take_damage(20, knockback_x, 300)
            create_damage_particles(enemy.x, enemy.y, 5)
            combo += 1
            combo_timer = 2.0
            score += 100 * combo
            max_combo = max(max_combo, combo)

    # Update combo system
    if combo_timer > 0:
        combo_timer -= dt
        if combo_timer <= 0:
            combo = 0

    # Update entities and particles
    player.update(dt, platforms)
    enemy.update(player, platforms, dt)
    particles.update(dt)

    # Check for level transition
    level_changed, exit_direction = check_level_transition(player, SCREEN_WIDTH)
    if level_changed:
        current_level += 1
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        reset_player_position(player, exit_direction, SCREEN_WIDTH)
        enemy.x = SCREEN_WIDTH // 2
        enemy.y = platforms[0].rect.top + 50  # Justo encima de la plataforma

    # Draw game state
    draw_gradient_background(screen)
    for platform in platforms:
        platform.draw(screen)
    
    # Draw entities with visual effects
    if player.invulnerable:
        if int(player.invulnerable_timer * 10) % 2:  # Blinking effect
            player.draw(screen)
    else:
        player.draw(screen)
        
    if enemy.invulnerable:
        if int(enemy.invulnerable_timer * 10) % 2:
            enemy.draw(screen)
    else:
        enemy.draw(screen)

    # Draw particles
    particles.draw(screen)

    # Draw UI
    font = pygame.font.SysFont(None, 36)
    # Health bars
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player.health/100), 20))
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH-210, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH-210, 10, 200 * (enemy.health/100), 20))
    
    # Score and combo
    score_text = font.render(f'Score: {score}', True, WHITE)
    combo_text = font.render(f'Combo: {combo}x', True, YELLOW if combo > 1 else WHITE)
    level_text = font.render(f'Level: {current_level}', True, WHITE)
    
    screen.blit(score_text, (10, 40))
    screen.blit(combo_text, (10, 80))
    screen.blit(level_text, (10, 120))

    # Show floating damage numbers
    if enemy.invulnerable:
        show_floating_text(screen, "20!", enemy.x, enemy.y + 50, RED, 30)

    # Check game over condition
    if player.health <= 0:
        show_game_over(screen, victory=False)
        running = False
    elif enemy.health <= 0:
        show_game_over(screen, victory=True)
        score += 1000 * current_level  # Level completion bonus
        enemy.health = enemy.max_health  # Reset enemy for next level
        current_level += 1
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        reset_player_position(player, "right", SCREEN_WIDTH)
        enemy.x = SCREEN_WIDTH // 2
        enemy.y = platforms[0].rect.top  # Posición directa sobre la plataforma
        enemy.velocity_y = 0  # Resetear velocidad vertical

    pygame.display.flip()

pygame.quit()
