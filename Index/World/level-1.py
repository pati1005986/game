import pygame
import sys
import os

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Index.Player.player import Player
from Index.World.style_worlds import draw_gradient_background  # Importa el fondo con gradiente
from Index.World.procedural_levels import generate_platforms  # Nueva generación procedural de plataformas
from Index.Enemies.enemie import Enemy

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platformer Level 1")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Variables de nivel
current_level = 1

# Initialize platforms first
platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)

# Create player and enemy instances and position them above their starting platforms
player_x, player_y = platforms[0].get_spawn_position()
enemy_x, enemy_y = platforms[1].get_spawn_position()

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
    enemy_x, enemy_y = platforms[1].get_spawn_position()
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

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses and animations
    keys = pygame.key.get_pressed()
    moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
    player.style.update_animation(dt, moving, player.is_jumping, player.is_attacking)
    
    if keys[pygame.K_LEFT]:
        player.move_left(dt)
    if keys[pygame.K_RIGHT]:
        player.move_right(dt)
    if keys[pygame.K_SPACE]:
        player.jump()
    if keys[pygame.K_a]:
        player.attack()

    # Update entities
    player.update(dt, platforms)
    enemy.update(player, platforms, dt)

    # Check if entities fell off the screen
    if player.y < -SCREEN_HEIGHT:
        current_level += 1
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        player.x, player.y = platforms[0].get_spawn_position()
        enemy.x, enemy.y = platforms[-1].get_spawn_position()

    # Draw game state
    draw_gradient_background(screen)
    for platform in platforms:
        platform.draw(screen)
    player.draw(screen)
    enemy.draw(screen)

    # Draw UI
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f'Salud: {player.health}', True, (255, 255, 255))
    screen.blit(health_text, (10, 10))

    # Check game over condition
    if player.health <= 0:
        show_game_over(screen, victory=False)
        running = False

    pygame.display.flip()

pygame.quit()
