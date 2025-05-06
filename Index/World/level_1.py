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
from Index.Utils.collision_helper import CollisionHelper

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
        self.particle_surfaces = {}
        self.max_particles = 200
        
    def _get_particle_surface(self, size: int, color: tuple) -> pygame.Surface:
        """Obtiene o crea una superficie pre-renderizada para partículas"""
        key = (size, color)
        if key not in self.particle_surfaces:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*color, 255), (size//2, size//2), size//2)
            self.particle_surfaces[key] = surf
        return self.particle_surfaces[key]
    
    def add_particle(self, x: float, y: float, color: tuple, velocity_x: float, 
                    velocity_y: float, lifetime: float = 1.0, size: int = 5):
        """Añade una nueva partícula si no se excede el límite"""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'x': x, 'y': y,
                'vx': velocity_x, 'vy': velocity_y,
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'size': size
            })
    
    def update(self, dt: float) -> None:
        """Actualiza todas las partículas con física optimizada"""
        # Actualizar en lote para mejor rendimiento
        for particle in self.particles[:]:
            # Actualizar posición con integración de Verlet
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['vy'] -= 500 * dt  # Gravedad
            
            # Actualizar tiempo de vida
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Dibuja las partículas con técnicas de renderizado optimizadas"""
        # Agrupar partículas por tamaño y color para minimizar cambios de superficie
        particle_groups = {}
        for particle in self.particles:
            key = (particle['size'], particle['color'])
            if key not in particle_groups:
                particle_groups[key] = []
            particle_groups[key].append(particle)
        
        # Dibujar cada grupo de partículas
        for (size, color), group in particle_groups.items():
            surface = self._get_particle_surface(size, color)
            
            # Dibujar todas las partículas del mismo tipo en lote
            for particle in group:
                # Calcular alpha basado en tiempo de vida
                alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
                if alpha > 0:
                    # Crear copia con alpha ajustado
                    temp_surf = surface.copy()
                    temp_surf.set_alpha(alpha)
                    
                    # Dibujar partícula
                    screen.blit(temp_surf,
                              (particle['x'] - size//2,
                               screen.get_height() - particle['y'] - size//2))
                               
    def create_explosion(self, x: float, y: float, color: tuple,
                        num_particles: int = 20, spread: float = 200):
        """Crea una explosión de partículas con efecto mejorado"""
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, spread)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(0.5, 1.5)
            size = random.randint(3, 7)
            self.add_particle(x, y, color, vx, vy, lifetime, size)

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.width = 20
        self.height = 20
        self.active = True
        self.collected = False
        self.effect_duration = 10.0
        self.animation_offset = 0
        self.float_speed = 2
        self.float_range = 10
        self.glow_intensity = 0
        self.particles = []
        self.time_active = 0
        
    def update(self, dt):
        self.time_active += dt
        
        # Animación flotante suave
        self.animation_offset = math.sin(self.time_active * self.float_speed) * self.float_range
        
        # Efecto de brillo pulsante
        self.glow_intensity = abs(math.sin(self.time_active * 3)) * 0.5
        
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle['lifetime'] -= dt
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
                continue
                
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['alpha'] = int(255 * (particle['lifetime'] / particle['max_lifetime']))
        
        # Generar nuevas partículas
        if random.random() < 0.1:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(20, 50)
            self.particles.append({
                'x': self.x + self.width/2,
                'y': self.y + self.height/2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.uniform(0.5, 1.0),
                'max_lifetime': 1.0,
                'alpha': 255
            })
        
    def draw(self, screen):
        if not self.active:
            return
            
        # Color según el tipo de power-up
        colors = {
            'speed': (255, 255, 0),    # Amarillo
            'jump': (0, 255, 0),       # Verde
            'shield': (0, 255, 255)    # Cian
        }
        base_color = colors[self.type]
        
        # Dibujar partículas
        for particle in self.particles:
            color = (*base_color, particle['alpha'])
            pos = (int(particle['x']), int(particle['y'] + self.animation_offset))
            pygame.draw.circle(screen, color, pos, 2)
        
        # Dibujar efecto de brillo
        glow_size = self.width + 10 + math.sin(self.time_active * 4) * 4
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        glow_color = (*base_color, int(128 * self.glow_intensity))
        pygame.draw.circle(glow_surface, glow_color,
                         (glow_size//2, glow_size//2), glow_size//2)
        
        # Posición con animación flotante
        y_pos = self.y + self.animation_offset
        screen.blit(glow_surface,
                   (self.x + self.width//2 - glow_size//2,
                    y_pos + self.height//2 - glow_size//2))
        
        # Dibujar power-up principal
        pygame.draw.rect(screen, base_color,
                        (self.x, y_pos, self.width, self.height))
        
        # Dibujar borde brillante con efecto pulsante
        border_color = tuple(min(255, c + int(100 * self.glow_intensity))
                           for c in base_color)
        pygame.draw.rect(screen, border_color,
                        (self.x, y_pos, self.width, self.height), 2)

# Añadir variables globales para power-ups
power_ups = []
active_effects = {
    'speed': 0,
    'jump': 0,
    'shield': 0
}

def spawn_power_up():
    """Generar un power-up aleatorio sobre la plataforma base"""
    if not platforms:
        return
        
    # Usar la plataforma base
    platform = platforms[0]
    
    # Elegir tipo aleatorio
    power_type = random.choice(['speed', 'jump', 'shield'])
    
    # Posición aleatoria sobre la plataforma base
    x = platform.rect.x + random.randint(50, platform.rect.width - 70)  # Margen de 50px a la izquierda y 70px a la derecha
    y = platform.rect.y - random.randint(100, 300)  # Entre 100 y 300 pixels sobre la plataforma
    
    power_ups.append(PowerUp(x, y, power_type))

def update_power_ups(dt):
    """Actualizar power-ups y sus efectos"""
    global active_effects
    
    # Actualizar power-ups existentes
    for power_up in power_ups[:]:
        power_up.update(dt)
        
        # Verificar colisión con jugador
        player_rect = pygame.Rect(player.x, player.y, player.style.width, player.style.height)
        power_up_rect = pygame.Rect(power_up.x, power_up.y, power_up.width, power_up.height)
        
        # Verificar colisión con enemigo
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.style.width, enemy.style.height)
        
        if power_up.active and not power_up.collected:
            if player_rect.colliderect(power_up_rect):
                apply_power_up(power_up, is_player=True)
                power_up.collected = True
                power_up.active = False
                power_ups.remove(power_up)
            elif enemy_rect.colliderect(power_up_rect):
                apply_power_up(power_up, is_player=False)
                power_up.collected = True
                power_up.active = False
                power_ups.remove(power_up)
    
    # Actualizar efectos activos del jugador
    for effect_type in active_effects:
        if active_effects[effect_type] > 0:
            active_effects[effect_type] -= dt
            
            # Desactivar efecto cuando expire
            if active_effects[effect_type] <= 0:
                remove_power_up_effect(effect_type, is_player=True)

def apply_power_up(power_up, is_player=True):
    """Aplicar efecto del power-up al jugador o enemigo"""
    if is_player:
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
    else:
        # Aplicar al enemigo
        enemy.apply_power_up(power_up.type, power_up.effect_duration)

def remove_power_up_effect(effect_type, is_player=True):
    """Remover efecto del power-up del jugador o enemigo"""
    if is_player:
        if effect_type == 'speed':
            player.max_velocity /= 1.5
            player.acceleration /= 1.5
        elif effect_type == 'jump':
            player.jump_power /= 1.3
        elif effect_type == 'shield':
            player.invulnerable = False
    else:
        enemy.remove_power_up_effect(effect_type)

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
    player_x = 100
    player_y = platforms[0].rect.top - 100  # Aparecer 100 pixels más arriba de la plataforma
    enemy_x = screen_width - 100  # Position enemy on the right side
    enemy_y = platforms[0].get_spawn_position()[1] - 300  # 300 pixels más arriba (valor negativo)
    return platforms, (player_x, player_y), (enemy_x, enemy_y)

def update_entities(player, enemy, platforms, dt):
    """Update all entities with optimized collision detection"""
    # Actualizar cuadrícula espacial con todas las entidades
    collision_helper = CollisionHelper()
    all_entities = [player, enemy] + platforms
    collision_helper.update_spatial_grid(all_entities)
    
    # Guardar posiciones anteriores para resolución de colisiones
    prev_player_y = player.y
    prev_enemy_y = enemy.y
    
    # Actualizar entidades
    player.update(dt)
    enemy.update(player, [], dt)
    
    # Manejar colisiones del jugador
    for platform in platforms:
        player_rect = pygame.Rect(player.x, player.y, player.style.width, player.style.height)
        if player_rect.colliderect(platform.rect):
            # Resolver colisión vertical
            if player.velocity_y >= 0:  # Cayendo
                if prev_player_y + player.style.height <= platform.rect.top:
                    player.y = platform.rect.top - player.style.height
                    player.velocity_y = 0
                    player.is_jumping = False
                    player.on_ground = True
            elif player.velocity_y < 0:  # Subiendo
                if prev_player_y >= platform.rect.bottom:
                    player.y = platform.rect.bottom
                    player.velocity_y = 0
    
    # Manejar colisiones del enemigo
    for platform in platforms:
        enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.style.width, enemy.style.height)
        if enemy_rect.colliderect(platform.rect):
            # Resolver colisión vertical
            if enemy.velocity_y >= 0:  # Cayendo
                if prev_enemy_y + enemy.style.height <= platform.rect.top:
                    enemy.y = platform.rect.top - enemy.style.height
                    enemy.velocity_y = 0
                    enemy.is_jumping = False
                    enemy.on_ground = True
            elif enemy.velocity_y < 0:  # Subiendo
                if prev_enemy_y >= platform.rect.bottom:
                    enemy.y = platform.rect.bottom
                    enemy.velocity_y = 0
    
# Verificar colisión entre jugador y enemigo
    if collision_helper.check_pixel_perfect_collision(player, enemy):
        enemy.check_player_collision(player)
    
    # Limpiar caché
    collision_helper.clear_cache()
    
    # Check for falls
    if check_entity_fall(player, SCREEN_HEIGHT):
        return True, False  # Player fell, game over
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
    player.y = platforms[0].rect.top - 100  # Aparecer 100 pixels más arriba de la plataforma
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
    player_y = platforms[0].rect.top - 100  # Aparecer 100 pixels más arriba de la plataforma
    enemy_x = SCREEN_WIDTH - 200
    enemy_y = platforms[0].rect.top - 300  # 300 pixels más arriba
    
    player = Player(x=player_x, y=player_y)
    enemy = Enemy(x=enemy_x, y=enemy_y)

def update_game_state(dt):
    global combo_timer, combo, current_level, platforms, score
    
    # Actualizar entidades con sistema de colisiones optimizado
    player_fell, enemy_fell = update_entities(player, enemy, platforms, dt)
    
    # Actualizar sistemas visuales
    particles.update(dt)
    for platform in platforms:
        platform.update(dt)
    
    # Actualizar power-ups y pasar la lista al enemigo
    update_power_ups(dt)
    enemy.update(player, platforms, dt, power_ups)  # Pasar power_ups al enemigo
    
    # Generar power-up aleatorio con más frecuencia
    if len(power_ups) < 3 and random.random() < 0.02:  # Aumentada probabilidad
        spawn_power_up()
    
    # Actualizar combo
    if combo_timer > 0:
        combo_timer -= dt
        if combo_timer <= 0:
            combo = 0
    
    # Manejar transiciones de nivel
    level_changed, exit_direction = check_level_transition(player, SCREEN_WIDTH)
    if level_changed:
        current_level += 1
        platforms = generate_platforms(current_level, SCREEN_WIDTH, SCREEN_HEIGHT)
        reset_player_position(player, exit_direction, SCREEN_WIDTH)
        enemy.x = SCREEN_WIDTH // 2
        enemy.y = platforms[0].rect.top - 300  # Aparecer más arriba que la plataforma

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
    enemy.y = platforms[0].rect.top - 300  # Aparecer más arriba que la plataforma
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
            # Input handling
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
                    particles.create_explosion(enemy.x, enemy.y, RED, 20, 200)
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
