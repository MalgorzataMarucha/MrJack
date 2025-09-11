import pygame
import numpy as np 
import mechanics.map as map

class Building:
    def __init__(self, position, passable=False, movable=False, revealing=False, can_stay_on = False):
        self.passable = passable
        self.movable = movable
        self.revealing = revealing
        self.position = position
        self.can_stay_on = can_stay_on

    def draw(self,surface, pos, icon):
        hex_width = int(2 * map.size_of_hex)
        hex_height = int(np.sqrt(3) * map.size_of_hex)

        scaled_icon = pygame.transform.smoothscale(icon, (hex_width, hex_height))

        overlay = pygame.Surface((hex_width, hex_height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 15))  # alpha np. 100

        scaled_icon.blit(overlay, (0, 0))

        mask_surface = pygame.Surface((hex_width, hex_height), pygame.SRCALPHA)
        center = (hex_width // 2, hex_height // 2)

        hex_dummy = map.Hex(0, 0, 0)
        corners = [hex_dummy.hex_corner(center, i) for i in range(6)]
        pygame.draw.polygon(mask_surface, (255, 255, 255, 255), corners)

        masked_icon = scaled_icon.copy()
        masked_icon.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        rect = masked_icon.get_rect(center=pos)
        surface.blit(masked_icon, rect)
    

class Apartaments(Building):
    def __init__(self, position):
         super().__init__(position, passable=False, movable=False, revealing=False, can_stay_on=False)

class Lantern(Building):
    def __init__(self, position):
         super().__init__(position, passable=False, movable=True, revealing=True, can_stay_on=False)

class Lantern_Off(Building):
    def __init__(self, position):
         super().__init__(position, passable=False, movable=True, revealing=False, can_stay_on=False)
    
class Closed_Sewer(Building):
    def __init__(self, position):
         super().__init__(position, passable=True, movable=True, revealing=False, can_stay_on = True)

    
class Police_Cordon(Building):
    def __init__(self, position):
         super().__init__(position, passable=False, movable=True, revealing=False, can_stay_on = False)


class Open_Sewer(Building):
    def __init__(self, position):
         super().__init__(position, passable=True, movable=True, revealing=False, can_stay_on = True)

    
def get_building_at(pos, building_list):
    return next((b for b in building_list if b.position == pos), None)
