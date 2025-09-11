import pygame
import numpy as np

size_of_hex = 40
color_of_hex = (192, 192, 192)
color_of_hex_outline = (0, 0, 0)
color_of_hex_outline_get_out = (255, 0, 0)

class Hex:
    def __init__(self, q, r, s):
        self.q = q
        self.r = r
        self.s = s

    def __eq__(self, other):
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def neighbors(self, hex_map):
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        results = []
        for dq, dr in directions:
            nq = self.q + dq
            nr = self.r + dr
            ns = -nq - nr
            neighbor = Hex(nq, nr, ns)
            if neighbor in hex_map:
                results.append(neighbor)
        return results

    
    def hex_to_pixel(self):
        x = (3./2 * self.q)
        y = (np.sqrt(3)/2 * self.q + np.sqrt(3) * self.r)
        x = x * size_of_hex
        y = y * size_of_hex
        return (x, y)

    def hex_corner(self, center, i):
        deg = 60 * i
        rad = np.pi / 180 * deg
        return (center[0] + size_of_hex * np.cos(rad), center[1] + size_of_hex * np.sin(rad))

    def draw(self, surface, offset_x=0, offset_y=0, building = 0):
        center = self.hex_to_pixel()
        center = (center[0] + offset_x, center[1] + offset_y)
        corners = [self.hex_corner(center, i) for i in range(6)]
        if building == 0:
            pygame.draw.polygon(surface, color_of_hex, corners)
            pygame.draw.polygon(surface, color_of_hex_outline, corners, 3)
        elif building == 1:
            pygame.draw.polygon(surface, color_of_hex_outline, corners, 3)
        else:
            pygame.draw.polygon(surface, color_of_hex_outline_get_out, corners, 3)

def hex_map_generator(col_row_hex, operations = None):
    hexes = []
    if operations:
        operations += 1
    for q, (r1, r2) in enumerate(col_row_hex):
        if operations:
            operations += 1
        for r in range(r1, r2):
            s = -q - r
            hexes.append(Hex(q, r, s))
            if operations:
                operations += 3
    return hexes



        
        



    