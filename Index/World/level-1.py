import pygame
import sys
import os
import random
import math
import time

# Agregar el directorio raíz del proyecto al sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from Index.Player.player import Player
from Index.World.style_worlds import draw_gradient_background
from Index.World.procedural_levels import generate_platforms
from Index.Enemies.enemie import Enemy
from Index.Menu.menu_system import Menu, Settings, change_screen_resolution

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

# Global variables
platforms = []
player = None
enemy = None
current_level = 1
score = 0
combo = 0
combo_timer = 0
max_combo = 0

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

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.width = 20
        self.height = 20
        self.active = True
        self.collected = False
        self.effect_duration = 10.0  # 10 segundos de duración
        self.animation_offset = 0
        self.float_speed = 2
        self.float_range = 10
        
    def update(self, dt):
        # Animación flotante
        self.animation_offset = math.sin(time.time() * self.float_speed) * self.float_range
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Color según el tipo de power-up
        colors = {
            'speed': (255, 255, 0),  # Amarillo para velocidad
            'jump': (0, 255, 0),     # Verde para salto
            'shield': (0, 255, 255)   # Cian para escudo
        }
        
        # Dibujar power-up con efecto flotante
        y_pos = self.y + self.animation_offset
        pygame.draw.rect(screen, colors[self.type],
                        (self.x, y_pos, self.width, self.height))
        
        # Dibujar borde brillante
        pygame.draw.rect(screen, WHITE,
                        (self.x, y_pos, self.width, self.height), 2)

# Añadir variables globales para power-ups
power_ups = []
active_effects = {
    'speed': 0,
    'jump': 0,
    'shield': 0
}

def spawn_power_up():
    """Generar un power-up aleatorio en una plataforma"""
    if len(platforms) < 2:
        return
        
    # Elegir plataforma aleatoria (excluyendo la base)
    platform = random.choice(platforms[1:])
    
    # Elegir tipo aleatorio
    power_type = random.choice(['speed', 'jump', 'shield'])
    
    # Posición en la plataforma
    x = platform.rect.x + random.randint(0, platform.rect.width - 20)
    y = platform.rect.y - 30
    
    power_ups.append(PowerUp(x, y, power_type))

def update_power_ups(dt):
    """Actualizar power-ups y sus efectos"""
    global active_effects
    
    # Actualizar power-ups existentes
    for power_up in power_ups[:]:
        power_up.update(dt)
        
        # Verificar colisión con jugador
        if power_up.active and not power_up.collected:
            player_rect = pygame.Rect(player.x, player.y, player.style.width, player.style.height)
            power_up_rect = pygame.Rect(power_up.x, power_up.y, power_up.width, power_up.height)
            
            if player_rect.colliderect(power_up_rect):
                apply_power_up(power_up)
                power_up.collected = True
                power_up.active = False
                power_ups.remove(power_up)
    
    # Actualizar efectos activos
    for effect_type in active_effects:
        if active_effects[effect_type] > 0:
            active_effects[effect_type] -= dt
            
            # Desactivar efecto cuando expire
            if active_effects[effect_type] <= 0:
                remove_power_up_effect(effect_type)

def apply_power_up(power_up):
    """Aplicar efecto del power-up"""
    global active_effects
    
    active_effects[power_up.type] = power_up.effect_duration
    
    if power_up.type == 'speed':
        player.max_velocity *= 1.5
        player.acceleration *= 1.5
    elif power_up.type == 'jump':
        player.jump_power *= 1.3
    elif power_up.type == 'shield':
        player.invulnerable = True
        player.invulnerable_timer = power_up.effect_duration

def remove_power_up_effect(effect_type):
    """Remover efecto del power-up"""
    if effect_type == 'speed':
        player.max_velocity /= 1.5
        player.acceleration /= 1.5
    elif effect_type == 'jump':
        player.jump_power /= 1.3
    elif effect_type == 'shield':
        player.invulnerable = False

def draw_power_up_effects(screen):
    """Dibujar efectos activos en la UI"""
    y_offset = 160  # Empezar debajo del score y combo
    
    for effect_type, duration in active_effects.items():
        if duration > 0:
            text = f"{effect_type.capitalize()}: {int(duration)}s"
            color = (255, 255, 0) if effect_type == 'speed' else \
                    (0, 255, 0) if effect_type == 'jump' else \
                    (0, 255, 255)
            
            text_surf = pygame.font.SysFont(None, 36).render(text, True, color)
            screen.blit(text_surf, (10, y_offset))
            y_offset += 30

# Initialize particles
particles = ParticleSystem()

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

def check_platform_collisions(entity, platforms, screen):
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

def initialize_game():
    global platforms, player, enemy, current_level, score, combo, combo_timer, max_combo
    current_level = 1
    score = 0
    combo = 0
    combo_timer = 0
    max_combo = 0
    
    platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
    player_x = 100
    player_y = platforms[0].rect.top
    enemy_x = SCREEN_WIDTH - 200
    enemy_y = platforms[0].rect.top
    
    player = Player(x=player_x, y=player_y)
    enemy = Enemy(x=enemy_x, y=enemy_y)

def update_game_state(dt):
    global combo_timer, combo, current_level, platforms
    player.update(dt, platforms)
    enemy.update(player, platforms, dt)
    particles.update(dt)
    
    # Actualizar power-ups
    update_power_ups(dt)
    
    # Generar power-up aleatorio
    if len(power_ups) < 3 and random.random() < 0.01:  # 1% de probabilidad por frame
        spawn_power_up()
    
    if combo_timer > 0:
        combo_timer -= dt
        if combo_timer <= 0:
            combo = 0
    
    level_changed, exit_direction = check_level_transition(player, SCREEN_WIDTH)
    if level_changed:
        current_level += 1
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        reset_player_position(player, exit_direction, SCREEN_WIDTH)
        enemy.x = SCREEN_WIDTH // 2
        enemy.y = platforms[0].rect.top + 50

def draw_game_state(screen):
    draw_gradient_background(screen)
    for platform in platforms:
        platform.draw(screen)
    
    # Dibujar power-ups
    for power_up in power_ups:
        power_up.draw(screen)
    
    if player.invulnerable:
        if int(player.invulnerable_timer * 10) % 2:
            player.draw(screen)
    else:
        player.draw(screen)
        
    if enemy.invulnerable:
        if int(enemy.invulnerable_timer * 10) % 2:
            enemy.draw(screen)
    else:
        enemy.draw(screen)
    
    particles.draw(screen)
    
    # Draw UI
    font = pygame.font.SysFont(None, 36)
    pygame.draw.rect(screen, RED, (10, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (10, 10, 200 * (player.health/100), 20))
    pygame.draw.rect(screen, RED, (SCREEN_WIDTH-210, 10, 200, 20))
    pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH-210, 10, 200 * (enemy.health/100), 20))
    
    score_text = font.render(f'Score: {score}', True, WHITE)
    combo_text = font.render(f'Combo: {combo}x', True, YELLOW if combo > 1 else WHITE)
    level_text = font.render(f'Level: {current_level}', True, WHITE)
    
    screen.blit(score_text, (10, 40))
    screen.blit(combo_text, (10, 80))
    screen.blit(level_text, (10, 120))
    
    # Dibujar efectos activos
    draw_power_up_effects(screen)
    
    if enemy.invulnerable:
        show_floating_text(screen, "20!", enemy.x, enemy.y + 50, RED, 30)

def reset_game_state():
    global platforms
    platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
    reset_player_position(player, "right", SCREEN_WIDTH)
    enemy.x = SCREEN_WIDTH // 2
    enemy.y = platforms[0].rect.top
    enemy.velocity_y = 0

def main():
    global score, combo, combo_timer, max_combo, current_level, SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mi Juego")
    clock = pygame.time.Clock()
    
    # Estados del juego
    MENU = 'menu'
    GAME = 'game'
    SETTINGS = 'settings'
    current_state = MENU
    
    # Inicializar componentes
    menu = Menu(screen)
    settings = Settings(screen)
    game_initialized = False
    current_difficulty = 1  # Normal por defecto
    
    # Guardar la resolución anterior antes de pantalla completa
    previous_resolution = (SCREEN_WIDTH, SCREEN_HEIGHT)
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == MENU:
                action = menu.handle_event(event)
                if action == 'play':
                    current_state = GAME
                    if not game_initialized:
                        initialize_game()
                        # Aplicar dificultad actual al enemigo
                        enemy.set_difficulty(current_difficulty)
                        game_initialized = True
                elif action == 'settings':
                    current_state = SETTINGS
                    settings = Settings(screen)
                    
            elif current_state == SETTINGS:
                action, value = settings.handle_event(event)
                if action == 'menu':
                    current_state = MENU
                    menu = Menu(screen)
                elif action == 'change_resolution':
                    screen = change_screen_resolution(screen, value)
                    SCREEN_WIDTH, SCREEN_HEIGHT = value
                    previous_resolution = value
                    settings = Settings(screen)
                    menu = Menu(screen)
                elif action == 'toggle_fullscreen':
                    if settings.is_fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        SCREEN_WIDTH = screen.get_width()
                        SCREEN_HEIGHT = screen.get_height()
                    else:
                        screen = pygame.display.set_mode(previous_resolution)
                        SCREEN_WIDTH, SCREEN_HEIGHT = previous_resolution
                    settings = Settings(screen)
                    menu = Menu(screen)
                elif action == 'change_difficulty':
                    current_difficulty = value
                    if enemy:  # Si el enemigo ya existe, actualizar su dificultad
                        enemy.set_difficulty(current_difficulty)
                    
            elif current_state == GAME:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        current_state = MENU
                    elif event.key == pygame.K_SPACE:
                        player.jump()
                    elif event.key == pygame.K_LSHIFT:
                        player.dash(dt)
        
        # Actualizar y dibujar según el estado actual
        if current_state == MENU:
            menu.draw(draw_gradient_background)
        elif current_state == SETTINGS:
            settings.draw(draw_gradient_background)
        elif current_state == GAME:
            # Lógica del juego existente
            keys = pygame.key.get_pressed()
            moving = keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]
            player.style.update_animation(dt, moving, player.is_jumping, player.is_attacking)
            
            if keys[pygame.K_LEFT]:
                player.move_left(dt)
            if keys[pygame.K_RIGHT]:
                player.move_right(dt)
            if keys[pygame.K_a]:
                player.attack()
                if abs(player.x - enemy.x) < 60 and abs(player.y - enemy.y) < 60:
                    knockback_x = 500 if player.facing_right else -500
                    enemy.take_damage(20, knockback_x, 300)
                    create_damage_particles(enemy.x, enemy.y, 5)
                    combo += 1
                    combo_timer = 2.0
                    score += 100 * combo
                    max_combo = max(max_combo, combo)
            
            # Update game state
            update_game_state(dt)
            # Draw game state
            draw_game_state(screen)
            
            if player.health <= 0:
                show_game_over(screen, victory=False)
                current_state = MENU
                game_initialized = False
            elif enemy.health <= 0:
                show_game_over(screen, victory=True)
                score += 1000 * current_level
                enemy.health = enemy.max_health
                current_level += 1
                reset_game_state()
        
        pygame.display.flip()

if __name__ == "__main__":
    main()
    pygame.quit()
