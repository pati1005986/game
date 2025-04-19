import pygame
from typing import List, Tuple, Dict, Set

class SpatialGrid:
    def __init__(self, cell_size: int = 64):
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set] = {}
        
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Obtiene la celda de la cuadrícula para una posición"""
        return (int(x // self.cell_size), int(y // self.cell_size))
        
    def _get_overlapping_cells(self, rect: pygame.Rect) -> List[Tuple[int, int]]:
        """Obtiene todas las celdas que intersectan con un rectángulo"""
        start_cell = self._get_cell(rect.left, rect.top)
        end_cell = self._get_cell(rect.right, rect.bottom)
        
        cells = []
        for x in range(start_cell[0], end_cell[0] + 1):
            for y in range(start_cell[1], end_cell[1] + 1):
                cells.append((x, y))
        return cells
        
    def add_object(self, obj: any, rect: pygame.Rect) -> None:
        """Añade un objeto a las celdas apropiadas de la cuadrícula"""
        cells = self._get_overlapping_cells(rect)
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(obj)
            
    def clear(self) -> None:
        """Limpia la cuadrícula espacial"""
        self.grid.clear()
        
    def get_nearby_objects(self, rect: pygame.Rect) -> Set:
        """Obtiene objetos cercanos que podrían colisionar"""
        cells = self._get_overlapping_cells(rect)
        nearby = set()
        for cell in cells:
            if cell in self.grid:
                nearby.update(self.grid[cell])
        return nearby

class CollisionHelper:
    def __init__(self):
        self.spatial_grid = SpatialGrid()
        self.mask_cache: Dict[str, pygame.mask.Mask] = {}
        
    @staticmethod
    def get_pixel_mask(sprite_data: List[str], width: int, height: int, pixel_size: int) -> pygame.mask.Mask:
        """Crear una máscara de colisión desde datos de pixel art"""
        mask_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y, row in enumerate(sprite_data):
            for x, pixel in enumerate(row):
                if pixel in ('X', 'A'):
                    pygame.draw.rect(mask_surface, (255, 255, 255, 255),
                                  (x * pixel_size, y * pixel_size, pixel_size, pixel_size))
        return pygame.mask.from_surface(mask_surface)

    def check_pixel_perfect_collision(self, entity1: any, entity2: any) -> bool:
        """Verificar colisión pixel-perfect entre dos entidades con caché"""
        try:
            # Obtener frames actuales de animación
            frame1 = entity1.style.animations[entity1.style.current_animation][entity1.style.current_frame]
            frame2 = entity2.style.animations[entity2.style.current_animation][entity2.style.current_frame]
            
            # Obtener tamaños de píxel
            pixel_size1 = getattr(entity1.style, 'pixel_size', 10)
            pixel_size2 = getattr(entity2.style, 'pixel_size', 10)
            
            # Generar claves únicas para el caché
            key1 = f"{entity1.style.current_animation}_{entity1.style.current_frame}"
            key2 = f"{entity2.style.current_animation}_{entity2.style.current_frame}"
            
            # Obtener o crear máscaras
            if key1 not in self.mask_cache:
                self.mask_cache[key1] = self.get_pixel_mask(
                    frame1, entity1.style.width, entity1.style.height, pixel_size1)
            if key2 not in self.mask_cache:
                self.mask_cache[key2] = self.get_pixel_mask(
                    frame2, entity2.style.width, entity2.style.height, pixel_size2)
                
            mask1 = self.mask_cache[key1]
            mask2 = self.mask_cache[key2]
            
            # Calcular offset
            offset = (
                int(entity2.x - entity1.x),
                int(entity2.y - entity1.y)
            )
            
            return mask1.overlap(mask2, offset) is not None
            
        except (AttributeError, KeyError, IndexError):
            # Fallback a colisión simple de rectángulos
            rect1 = pygame.Rect(entity1.x, entity1.y, entity1.style.width, entity1.style.height)
            rect2 = pygame.Rect(entity2.x, entity2.y, entity2.style.width, entity2.style.height)
            return rect1.colliderect(rect2)

    def _get_entity_rect(self, entity) -> pygame.Rect:
        """Obtiene el rectángulo de colisión de una entidad, manejando diferentes tipos"""
        try:
            # Primero intentar obtener el rect directamente
            if hasattr(entity, 'rect'):
                return entity.rect
            # Si no tiene rect, intentar construirlo desde x,y y dimensiones
            elif hasattr(entity, 'x') and hasattr(entity, 'y'):
                width = getattr(entity.style, 'width', entity.width)
                height = getattr(entity.style, 'height', entity.height)
                return pygame.Rect(entity.x, entity.y, width, height)
        except AttributeError:
            # Si algo falla, retornar None
            return None

    def update_spatial_grid(self, entities: List[any]) -> None:
        """Actualiza la cuadrícula espacial con las entidades actuales"""
        self.spatial_grid.clear()
        for entity in entities:
            rect = self._get_entity_rect(entity)
            if rect is not None:
                self.spatial_grid.add_object(entity, rect)

    def get_potential_collisions(self, entity: any) -> Set:
        """Obtiene posibles colisiones usando la cuadrícula espacial"""
        rect = self._get_entity_rect(entity)
        if rect is not None:
            return self.spatial_grid.get_nearby_objects(rect)
        return set()

    def get_collision_normal(self, entity: any, platform: any) -> Tuple[Tuple[int, int], float]:
        """Obtiene la normal de colisión y profundidad de penetración"""
        entity_rect = self._get_entity_rect(entity)
        platform_rect = self._get_entity_rect(platform)
        
        if entity_rect is None or platform_rect is None:
            return (0, 0), 0
        
        # Calcular superposición en cada eje
        left_overlap = entity_rect.right - platform_rect.left
        right_overlap = platform_rect.right - entity_rect.left
        top_overlap = entity_rect.bottom - platform_rect.top
        bottom_overlap = platform_rect.bottom - entity_rect.top
        
        # Encontrar la mínima superposición
        overlaps = [
            (abs(left_overlap), (-1, 0), left_overlap),   # Normal izquierda
            (abs(right_overlap), (1, 0), right_overlap),  # Normal derecha
            (abs(top_overlap), (0, -1), top_overlap),     # Normal superior
            (abs(bottom_overlap), (0, 1), bottom_overlap) # Normal inferior
        ]
        
        min_overlap = min(overlaps, key=lambda x: x[0])
        return min_overlap[1], min_overlap[2]  # Retorna (normal, profundidad)

    def clear_cache(self) -> None:
        """Limpia el caché de máscaras"""
        self.mask_cache.clear()