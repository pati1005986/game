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

def show_game_over(screen):
    """Mostrar pantalla de Game Over"""
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render('Game Over', True, (255, 0, 0))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Esperar 3 segundos antes de salir

# Main game loop
running = True
while running:
    dt = clock.tick(60) / 1000.0  # Convert to seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses and animations
    keys = pygame.key.get_pressed()
    moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
    player.style.update_animation(dt, moving, player.is_jumping, player.is_attacking)
    
    if keys[pygame.K_LEFT]:
        player.move_left()
    if keys[pygame.K_RIGHT]:
        player.move_right()
    if keys[pygame.K_SPACE]:
        player.jump()
    if keys[pygame.K_a]:
        player.attack()

    # Update entities
    player.update(dt, platforms)
    enemy.update(player, platforms, dt)

    # Detectar si el jugador cae fuera de la pantalla (parte posterior)
    if player.y > SCREEN_HEIGHT:
        current_level += 1  # Incrementar el nivel
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        # Reiniciar posición del jugador y enemigo
        player_x, player_y = platforms[0].get_spawn_position()
        enemy_x, enemy_y = platforms[1].get_spawn_position()
        player.x, player.y = player_x, player_y
        enemy.x, enemy.y = enemy_x, enemy_y

    # Clear the screen con fondo de gradiente definido en los estilos
    draw_gradient_background(screen)

    # Draw platforms
    for platform in platforms:
        platform.draw(screen)

    # Draw player using the new draw method
    player.draw(screen)

    # Draw enemy
    enemy.draw(screen)

    # Mostrar la salud del jugador
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f'Salud: {player.health}', True, (255, 255, 255))
    screen.blit(health_text, (10, 10))

    # Verificar si la salud del jugador es 0 y mostrar Game Over
    if player.health <= 0:
        show_game_over(screen)
        running = False

    # Update the display
    pygame.display.flip()

pygame.quit()
