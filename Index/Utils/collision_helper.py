import pygame

class CollisionHelper:
    @staticmethod
    def get_pixel_mask(sprite_data, width, height, pixel_size):
        """Create a collision mask from pixel art data"""
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y, row in enumerate(sprite_data):
            for x, pixel in enumerate(row):
                if pixel in ('X', 'A'):
                    pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                                  (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        return pygame.mask.from_surface(mask_surface)

    @staticmethod
    def check_pixel_perfect_collision(entity1, entity2):
        """Check for pixel-perfect collision between two entities"""
        try:
            # Get current animation frames
            frame1 = entity1.style.animations[entity1.style.current_animation][entity1.style.current_frame]
            frame2 = entity2.style.animations[entity2.style.current_animation][entity2.style.current_frame]
            
            # Get pixel sizes, defaulting to 10 if not specified
            pixel_size1 = getattr(entity1.style, 'pixel_size', 10)
            pixel_size2 = getattr(entity2.style, 'pixel_size', 10)
            
            # Create masks
            mask1 = CollisionHelper.get_pixel_mask(frame1, entity1.style.width, entity1.style.height, pixel_size1)
            mask2 = CollisionHelper.get_pixel_mask(frame2, entity2.style.width, entity2.style.height, pixel_size2)
            
            # Calculate offset
            offset = (
                int(entity2.x - entity1.x),
                int(entity2.y - entity1.y)
            )
            
            return mask1.overlap(mask2, offset) is not None
        except (AttributeError, KeyError, IndexError):
            # Fallback to simple rectangle collision if pixel-perfect fails
            rect1 = pygame.Rect(entity1.x, entity1.y, entity1.style.width, entity1.style.height)
            rect2 = pygame.Rect(entity2.x, entity2.y, entity2.style.width, entity2.style.height)
            return rect1.colliderect(rect2)

    @staticmethod
    def get_collision_normal(entity, platform):
        """Get collision normal and penetration depth"""
        entity_rect = pygame.Rect(entity.x, entity.y, entity.style.width, entity.style.height)
        
        # Calculate overlap on each axis
        left_overlap = entity_rect.right - platform.rect.left
        right_overlap = platform.rect.right - entity_rect.left
        top_overlap = entity_rect.bottom - platform.rect.top
        bottom_overlap = platform.rect.bottom - entity_rect.top
        
        # Find minimum overlap
        overlaps = [
            (abs(left_overlap), (-1, 0)),   # Left normal
            (abs(right_overlap), (1, 0)),    # Right normal
            (abs(top_overlap), (0, -1)),     # Top normal
            (abs(bottom_overlap), (0, 1))    # Bottom normal
        ]
        
        # Return the normal with minimum overlap
        min_overlap = min(overlaps, key=lambda x: x[0])
        return min_overlap[1], min_overlap[0]