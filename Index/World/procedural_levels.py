import random
import pygame

class Platform:
    collision_margin = 10

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visual_rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 0), self.visual_rect)

    def get_spawn_position(self):
        """Returns a valid spawn position above this platform"""
        return self.rect.x + self.rect.width // 2, self.rect.top - Platform.collision_margin

def generate_platforms(level, screen_width, screen_height):
    platforms = []
    num_platforms = 5 + level
    platform_width = 200
    platform_height = 20
    margin = 50
    vertical_spacing = (screen_height - 200) // (num_platforms - 1)

    # First platform for player spawn (higher up)
    platforms.append(Platform(margin, screen_height - 150, platform_width, platform_height))

    # Second platform for enemy spawn (on the other side)
    platforms.append(Platform(screen_width - margin - platform_width, screen_height - 150, platform_width, platform_height))

    # Generate remaining platforms with better vertical distribution
    for i in range(num_platforms - 2):
        y = screen_height - 150 - (i + 1) * vertical_spacing
        x = random.randint(margin, screen_width - platform_width - margin)
        new_platform = Platform(x, y, platform_width, platform_height)
        
        # Check for overlaps
        if not any(new_platform.rect.colliderect(p.rect) for p in platforms):
            platforms.append(new_platform)

    return platforms
