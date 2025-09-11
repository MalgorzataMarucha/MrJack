import mechanics.map as map
from collections import deque
import numpy as np
import settings
import heapq
from mechanics.buildings import Police_Cordon, Open_Sewer, Lantern_Off, Lantern

def get_neighbors(pos, hex_set, distance = 1):
    directions = [(+distance, 0), (+distance, -distance), (0, -distance), (-distance, 0), (-distance, +distance), (0, +distance)]
    neighbors = [(pos[0] + dq, pos[1] + dr) for dq, dr in directions]
    if settings.operations:
        settings.operations += 1 + len(directions)
    return [n for n in neighbors if map.Hex(n[0], n[1], -n[0]-n[1]) in hex_set]

def hex_distance(a, b):
    if settings.operations:
        settings.operations += 1
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs((-a[0]-a[1]) - (-b[0]-b[1])))

def find_closest_escape_hex(character):
    start = character.position
    blocked = {b.position for b in settings.building_list if isinstance(b, Police_Cordon)}
    escape_hexes = [h for h in settings.get_out_hex if h not in blocked]
    sorted_escape_hexes = sorted(escape_hexes, key=lambda h: hex_distance(start, h))
    if settings.operations:
        settings.operations += 1 + len(settings.building_list)+ len(settings.get_out_hex) + len(escape_hexes) * np.log2(len(escape_hexes))
    return sorted_escape_hexes

def find_closest_building(position, type_of_building):
    buildings_positions = [b.position for b in settings.building_list if isinstance(b, type_of_building)]
    sorted_buildings = sorted(buildings_positions, key=lambda h: hex_distance(position, h))
    if settings.operations:
        settings.operations += len(settings.building_list) + len(buildings_positions) * np.log2(len(buildings_positions))
    return sorted_buildings

def find_closest_character(character = None, reversed = False, building_pos = None):
    if character:
        occupied_positions = [c.position for c in settings.character_list if character and c != character]
        sorted_positions = sorted(occupied_positions, key=lambda h: hex_distance(character.position, h), reverse = reversed)
        if settings.operations:
            settings.operations += len(settings.character_list) + len(occupied_positions) * np.log2(len(occupied_positions))
    elif building_pos:
        occupied_positions = [c.position for c in settings.character_list]
        sorted_positions = sorted(occupied_positions, key=lambda h: hex_distance(building_pos, h), reverse = reversed)
        if settings.operations:
            settings.operations += len(settings.character_list) + len(occupied_positions) * np.log2(len(occupied_positions))
    sorted_characters = []
    if settings.operations:
        settings.operations += 1
    for pos in sorted_positions:
        if settings.operations:
            settings.operations += 1
        for char in settings.character_list:
            if settings.operations:
                settings.operations += 1
            if pos == char.position:
                sorted_characters.append(char)
                if settings.operations:
                    settings.operations += 1
                
    return sorted_characters

def get_accessible_hexes(character, player, hex_map, max_steps, buildings, forbidden_positions):
    visited = set()
    queue = deque()
    q, r = character.position
    s = -q - r
    start = map.Hex(q, r, s)

    queue.append((start, 0))
    visited.add((q, r))

    accessible = {} 

    if settings.operations:
        settings.operations += 8 

    while queue:
        current, steps = queue.popleft()
        if settings.operations:
            settings.operations += 1
        if steps > max_steps:
            continue

        pos = (current.q, current.r)
        if settings.operations:
            settings.operations += 1

        if pos in forbidden_positions:
            if not (character == settings.murderer and player == "Jack" and not settings.Jack_visibility):
                continue

        building = next((b for b in buildings if b.position == pos), None)
        if settings.operations:
            settings.operations += len(buildings)
        if building and not building.passable:
            continue

        if pos != (q, r): 
            accessible[pos] = steps
            if settings.operations:
                settings.operations += 1
            

        for neighbor in current.neighbors(hex_map):
            coord = (neighbor.q, neighbor.r)
            if settings.operations:
                settings.operations += 2
            if coord in visited:
                continue
            elif coord in forbidden_positions:
                if not (character == settings.murderer and player == "Jack" and not settings.Jack_visibility):
                    continue

            neighbor_building = next((b for b in buildings if b.position == coord), None)
            if settings.operations:
                settings.operations += len(buildings)
            if neighbor_building is None or neighbor_building.passable:
                visited.add(coord)
                queue.append((neighbor, steps + 1))
                if settings.operations:
                    settings.operations += 2

    return accessible

def get_valid_end_positions(player, character, hexes_with_costs, occupied_positions, forbidden_positions, buildings, allow_shared_sewers=False, remaining_moves=0):
    import mechanics.deck as deck
    valid_positions = []
    open_sewers = [
    b.position for b in settings.building_list if isinstance(b, Open_Sewer) and b.position != character.position]
    if settings.operations:
        settings.operations += 1 + len(settings.building_list)

    for pos, cost in hexes_with_costs.items():
        is_occupied = pos in occupied_positions
        is_open_sewer = pos in open_sewers

        if settings.operations:
            settings.operations += 3

        if cost > remaining_moves:
            continue  

        if is_occupied:
            if not (player == "Detective" and len(deck.suspect_list) == 1 and pos == settings.murderer.position and character != settings.murderer):
                continue
            if (allow_shared_sewers and is_open_sewer and remaining_moves - cost >= 1):
                continue
            

        if pos in forbidden_positions:
            if not (character == settings.murderer and player == "Jack" and not settings.Jack_visibility):
                continue

        building = next((b for b in buildings if b.position == pos), None)
        if settings.operations:
            settings.operations += len(buildings)
        if building and not building.can_stay_on:
            continue



        valid_positions.append((pos, cost))
        if settings.operations:
            settings.operations += 1

    return valid_positions

def a_star(start, goal, impassable_positions, hex_set):
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    if settings.operations:
        settings.operations += 3 + len(open_set)
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if settings.operations:
            settings.operations += 1
        if current == goal:
            path = [current]
            if settings.operations:
                settings.operations += 1
            while current in came_from:
                current = came_from[current]
                path.append(current)
                if settings.operations:
                    settings.operations += 2
            path.reverse()
            if settings.operations:
                settings.operations += len(path)
            return path

        for neighbor in get_neighbors(current, hex_set):
            if settings.operations:
                settings.operations += 1
            if neighbor in impassable_positions:
                continue

            tentative_g_score = g_score[current] + 1
            if settings.operations:
                settings.operations += 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + hex_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                if settings.operations:
                    settings.operations += 4 + len(open_set)

    return None

def find_closest_path(character, goal, teleport=True):
    
    start = character.position
    impassable = {b.position for b in settings.building_list if not b.passable}
    path = []
    path.clear()

    open_sewers = [b.position for b in settings.building_list if isinstance(b, Open_Sewer)]

    normal_path = a_star(start, goal, impassable, settings.hex_map)
    normal_cost = len(normal_path) if normal_path else float('inf')
    if settings.operations:
        settings.operations += 2 + 2* len(settings.building_list) + len(settings.hex_map) + len(path)

    if teleport:
        best_teleport_cost = float('inf')
        best_path_to_sewer = None
        best_path_from_sewer = None
        if settings.operations:
            settings.operations += 3
        for entry_sewer in open_sewers:
            path_to_entry = a_star(start, entry_sewer, impassable, settings.hex_map)
            if settings.operations:
                settings.operations += 1
            if not path_to_entry:
                continue

            for exit_sewer in open_sewers:
                if settings.operations:
                    settings.operations += 1
                if exit_sewer == entry_sewer:
                    continue
                
                path_from_exit = a_star(exit_sewer, goal, impassable, settings.hex_map)
                if not path_from_exit:
                    continue

                total_cost = len(path_to_entry) + len(path_from_exit) - 1 
                if settings.operations:
                    settings.operations += 1

                if total_cost < best_teleport_cost:
                    best_teleport_cost = total_cost
                    best_path_to_sewer = path_to_entry
                    best_path_from_sewer = path_from_exit
                    if settings.operations:
                        settings.operations += 3

        if best_teleport_cost < normal_cost:
            path.append(best_path_to_sewer)
            path.append(best_path_from_sewer)
            if settings.operations:
                settings.operations += 2
        else:
            path.append(normal_path)
            if settings.operations:
                settings.operations += 1
    else:
         path.append(normal_path)
         if settings.operations:
            settings.operations += 1

    return path

def find_path(watson_position, neighbors, hex_set, building_list, target_condition=None, fallback=False):
    for neighbor in neighbors:
        dq = neighbor[0] - watson_position[0]
        dr = neighbor[1] - watson_position[1]

        current_q, current_r = neighbor
        current_path = []
        if settings.operations:
            settings.operations += 5

        while True:
            current_hex = map.Hex(current_q, current_r, -current_q - current_r)
            if settings.operations:
                settings.operations += 1
            if current_hex not in hex_set:
                break

            blocking = next((b for b in building_list
                             if b.position == (current_q, current_r) and not b.passable), None)
            
            if settings.operations:
                settings.operations += len(building_list)

            if blocking:
                break

            if (target_condition and target_condition((current_q, current_r))) or fallback:
                current_path.append((current_q, current_r))
                if settings.operations:
                    settings.operations += 1

            current_q += dq
            current_r += dr
            if settings.operations:
                settings.operations += 2

        if current_path:
            settings.Watsons_lamp_path.clear()
            settings.Watsons_lamp_path.append(current_path)
            if settings.operations:
                settings.operations += len(settings.Watsons_lamp_path) + 1
            return (current_path, (dq, dr))
    
    return ([], None)

def find_building(building_type, positions, multiple=True):
    if not isinstance(positions, (list, set, tuple)):
        positions = [positions]
        if settings.operations:
            settings.operations += 1
        
                
    if multiple:
        return next((b for b in settings.building_list if isinstance(b, building_type) and b.position in positions), None)
    else:
        return next((b for b in settings.building_list if isinstance(b, building_type) and b.position == positions), None)

def prepare_lanterns():
    for hex in settings.get_out_hex:
        lamp = find_closest_building(hex, Lantern)
        settings.lamps_to_turn_off.append(lamp[0])
        

def lanterns_off(round):
    if round <= len(settings.lamps_to_turn_off):
        pos = settings.lamps_to_turn_off[round - 1]
        building = next(
            (b for b in settings.building_list if isinstance(b, Lantern) and b.position == pos),
            None
        )
        if settings.operations:
            settings.operations += 1 + len(settings.building_list)
        if building:
            settings.building_list.remove(building)
            settings.building_list.append(Lantern_Off(pos))
            if settings.operations:
                settings.operations += len(settings.building_list) + 1
    return None