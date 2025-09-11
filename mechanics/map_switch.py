import random
import mechanics.buildings
import numpy as np
import mechanics.map_utils as map_utils
import mechanics.map
def increase_the_map(col_row_hex, amount):
    if amount > 0:
        for _ in range(amount):
            higher_pos_left = random.choice([True, False])
            higher_pos_right = random.choice([True, False])
            if higher_pos_left:
                col_row_hex.insert(0,[col_row_hex[0][0], col_row_hex[0][1]])
            else:
                col_row_hex.insert(0,[col_row_hex[0][0] + 1, col_row_hex[0][1] + 1])

            if higher_pos_right:
                col_row_hex.append([col_row_hex[-1][0] - 1, col_row_hex[-1][1] - 1])
            else:
                col_row_hex.append([col_row_hex[-1][0], col_row_hex[-1][1]])


        for column in col_row_hex:
            column[0] -= amount
            column[-1] += amount
        
        
def get_random_free_hex(hex_map, occupied):
    free_hexes = [h for h in hex_map if (h.q, h.r) not in occupied]
    if not free_hexes:
        return None
    
    choice = random.choice(free_hexes)
    return (choice.q, choice.r)
   
def prepare_the_map(amount, buildings, characters, get_away_hex):
    pos_for_cordons = 1
    if amount > 0:
        for build in buildings:
            if isinstance(build, mechanics.buildings.Police_Cordon):
                build.position = get_away_hex[pos_for_cordons]
                pos_for_cordons += 1
            else:
                build.position = (build.position[0] + amount, build.position[1])

        for char in characters:
            char.position = (char.position[0] + amount, char.position[1])

def scale_amount_of_items(amount,buildings, type_of_item):
    actual_number =  len({b.position for b in buildings if isinstance(b, type_of_item)})
    return ((1+amount/2) * actual_number - actual_number)

def get_ring(pos, distance, hex_set):
    directions = [(+1, 0), (+1, -1), (0, -1),
                  (-1, 0), (-1, +1), (0, +1)]
    results = []
    # startujemy na "narożniku pierścienia"
    q, r = pos[0] + directions[4][0] * distance, pos[1] + directions[4][1] * distance
    for i in range(6):  # 6 boków
        for _ in range(distance):
            candidate = (q, r)
            if mechanics.map.Hex(q, r, -q-r) in hex_set:
                results.append(candidate)
            # przesuwamy się po krawędzi pierścienia
            q += directions[i][0]
            r += directions[i][1]
    return results

def check_building(amount, new_pos, distance, type_of_build, buildings, get_away_hex):
    from settings import character_list, building_list
    to_remove = None
    if amount > 0:
        building_list.append(type_of_build(new_pos))
        amount -= 1
        return amount, to_remove
    else:
        list_of_builds = [b for b in building_list if isinstance(b, type_of_build)]
        random.shuffle(list_of_builds)
        for build in list_of_builds:
            too_close_to_escape = any(map_utils.hex_distance(build.position, escape_hex) == distance for escape_hex in get_away_hex)
            too_close_to_char = any(map_utils.hex_distance(build.position, char.position) == 1 for char in character_list)
            if not too_close_to_char and not too_close_to_escape:
                to_remove = build.position
                build.position = new_pos
                return amount, to_remove

    

def prepare_buildings(amount, buildings, characters, get_away_hex, hex_map):
    #preparation is needed only if the map is going to be increased
    if amount > 0:
        occupied = {b.position for b in buildings} 
        occupied_by_characters = {c.position for c in characters} 
        new_apartaments =  np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Apartaments))
        new_opened_sewers = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Open_Sewer))
        new_closed_sewers = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Closed_Sewer))
        new_lanterns_on = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Lantern))
        new_lanterns_off = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Lantern_Off))
        
        #preparing exits with proper buildings (lanterns, sewers, apartaments)
        for escape in get_away_hex:
            hexes_2 = get_ring(escape, 2, hex_map)
            hexes_1 = get_ring(escape,1, hex_map)
            lanterns_in_ring = [b for b in buildings if isinstance(b, mechanics.buildings.Lantern) and b.position in hexes_2]
            opened_sewers_in_ring = [b for b in buildings if isinstance(b, mechanics.buildings.Open_Sewer) and b.position in hexes_2]
            closed_sewer_in_ring = [b for b in buildings if isinstance(b, mechanics.buildings.Closed_Sewer) and b.position in hexes_2]
            apartaments_in_ring = [b for b in buildings if isinstance(b, mechanics.buildings.Apartaments) and b.position in hexes_1]
            placed = False
            #checking if lantern is already good positioned
            if lanterns_in_ring:
                #checking if eventually sewers need to be added
                if not opened_sewers_in_ring and not closed_sewer_in_ring:
                    for lantern in lanterns_in_ring:
                        neighbors = map_utils.get_neighbors(lantern.position, hex_map)
                        for neighbor in neighbors:
                            if neighbor in hexes_2 and neighbor not in occupied:
                                if get_away_hex.index(escape) in (0, 3):
                                    new_opened_sewers, to_remove = check_building(new_opened_sewers, neighbor, 2, mechanics.buildings.Open_Sewer, buildings, get_away_hex)
                                else:
                                    new_closed_sewers, to_remove = check_building(new_closed_sewers, neighbor, 2, mechanics.buildings.Closed_Sewer, buildings, get_away_hex)
                                placed = True
                                occupied.add(neighbor)
                                if to_remove:
                                    occupied.remove(to_remove)
                            if placed:
                                break
                        if placed:
                            break
                else:
                    continue
            #checking if at least any sewers are good positioned
            else:
                if opened_sewers_in_ring:
                    for sewer in opened_sewers_in_ring:
                        neighbors = map_utils.get_neighbors(sewer.position, hex_map)
                        for neighbor in neighbors:
                            if neighbor in hexes_2 and neighbor not in occupied:
                                new_lanterns_on, to_remove = check_building(new_lanterns_on, neighbor, 2, mechanics.buildings.Lantern, buildings, get_away_hex)
                                occupied.add(neighbor)
                                placed = True
                                if to_remove:
                                     occupied.remove(to_remove)
                            if placed:
                                break
                        if placed:
                            break
                elif closed_sewer_in_ring:
                    for sewer in closed_sewer_in_ring:
                        neighbors = map_utils.get_neighbors(sewer.position, hex_map)
                        for neighbor in neighbors:
                            if neighbor in hexes_2 and neighbor not in occupied:
                                new_lanterns_on, to_remove = check_building(new_lanterns_on, neighbor, 2, mechanics.buildings.Lantern, buildings, get_away_hex)
                                occupied.add(neighbor)
                                placed = True
                                if to_remove:
                                    occupied.remove(to_remove)
                            
                            if placed:
                                break

                        if placed:
                            break
                #if no sewers nor lantern, let's just put them 2 hexes away from exit and next to each other
                else:
                    random.shuffle(hexes_2)
                    for hex in hexes_2:
                        if hex not in occupied: 
                            neighbors = map_utils.get_neighbors(hex, hex_map)
                            random.shuffle(neighbors)
                            for neighbor in neighbors:
                                if neighbor in hexes_2 and neighbor not in occupied:
                                    new_lanterns_on, to_remove = check_building(new_lanterns_on, hex, 2, mechanics.buildings.Lantern, buildings, get_away_hex)
                                    occupied.add(hex)
                                    if to_remove:
                                        occupied.remove(to_remove)


                                    if get_away_hex.index(escape) in (0,3):
                                        new_opened_sewers, to_remove = check_building(new_opened_sewers, neighbor, 2, mechanics.buildings.Open_Sewer, buildings, get_away_hex)
                                    else:
                                        new_closed_sewers, to_remove = check_building(new_closed_sewers, neighbor, 2, mechanics.buildings.Closed_Sewer, buildings, get_away_hex)
                                    occupied.add(neighbor)
                                    if to_remove:
                                        occupied.remove(to_remove)
                                    placed = True
                                if placed:
                                    break
                        if placed:
                            break    
            #checking if at least 1 apartament is next to exit, if not - it's going to be added
            random.shuffle(hexes_1)
            if apartaments_in_ring:
                continue
            else:
                for hex in hexes_1:
                    if hex not in occupied:
                        new_apartaments, to_remove = check_building(new_apartaments, hex, 1, mechanics.buildings.Apartaments, buildings, get_away_hex)
                        occupied.add(hex)
                        if to_remove:
                            occupied.remove(to_remove)
                        break

    #for turned off lanterns
        while new_lanterns_off > 0:
            
            hex_picked = get_random_free_hex(hex_map, occupied)
            if (hex_picked not in occupied and hex_picked not in occupied_by_characters
            and not any(map_utils.hex_distance(hex_picked, escape_hex) <= 2 for escape_hex in get_away_hex)):
                
                buildings.append(mechanics.buildings.Lantern_Off(hex_picked))
                new_lanterns_off -= 1
                occupied.add(hex_picked)
                neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                placed = False
                for neighbor in neighbors:
                    if neighbor not in occupied:
                        if new_closed_sewers > 0:
                            buildings.append(mechanics.buildings.Closed_Sewer(neighbor))
                            new_closed_sewers -= 1
                            placed = True
                            occupied.add(neighbor)
                        elif new_opened_sewers > 0:
                            buildings.append(mechanics.buildings.Open_Sewer(neighbor))
                            new_opened_sewers -= 1
                            placed = True
                            occupied.add(neighbor)
                        elif new_apartaments > 0 and neighbor not in occupied_by_characters:
                            buildings.append(mechanics.buildings.Apartaments(neighbor))
                            new_apartaments -= 1
                            placed = True
                            occupied.add(neighbor)

                        
                        
                        if placed:
                            break

        while new_closed_sewers > 0:
            hex_picked = get_random_free_hex(hex_map, occupied)
            if (hex_picked not in occupied 
            and not any(map_utils.hex_distance(hex_picked, escape_hex) <= 2 for escape_hex in get_away_hex)):    
                buildings.append(mechanics.buildings.Closed_Sewer(hex_picked))
                new_closed_sewers -= 1
                occupied.add(hex_picked)
                neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                for neighbor in neighbors:
                    if neighbor not in occupied and neighbor not in occupied_by_characters and new_apartaments > 0:
                        buildings.append(mechanics.buildings.Apartaments(neighbor))
                        new_apartaments -= 1
                        break

        attempt = 0                        
        while new_lanterns_on > 0:
            hex_picked = get_random_free_hex(hex_map, occupied)
            attempt += 1
            if attempt < len(hex_map):
                if (hex_picked not in occupied and hex_picked not in occupied_by_characters 
                and all(neigh not in occupied_by_characters for neigh in map_utils.get_neighbors(hex_picked, hex_map))
                and all(neigh not in occupied for neigh in map_utils.get_neighbors(hex_picked, hex_map))):
                    buildings.append(mechanics.buildings.Lantern(hex_picked))
                    new_lanterns_on -= 1
                    occupied.add(hex_picked)
                    neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                    placed = False
                    for neighbor in neighbors:
                        if neighbor not in occupied:
                            if new_opened_sewers > 0:
                                buildings.append(mechanics.buildings.Open_Sewer(neighbor))
                                new_opened_sewers -= 1
                            elif new_apartaments > 0 and neighbor not in occupied_by_characters:
                                buildings.append(mechanics.buildings.Apartaments(neighbor))
                                new_apartaments -= 1
                            placed = True
                            occupied.add(neighbor)
                            
                            if placed:
                                break   
            else:
                if (hex_picked not in occupied and hex_picked not in occupied_by_characters 
                and all(neigh not in occupied_by_characters for neigh in map_utils.get_neighbors(hex_picked, hex_map))):
                    buildings.append(mechanics.buildings.Lantern(hex_picked))
                    new_lanterns_on -= 1
                    occupied.add(hex_picked)
                    neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                    placed = False
                    for neighbor in neighbors:
                        if neighbor not in occupied:
                            if new_opened_sewers > 0:
                                buildings.append(mechanics.buildings.Open_Sewer(neighbor))
                                new_opened_sewers -= 1
                            elif new_apartaments > 0 and neighbor not in occupied_by_characters:
                                buildings.append(mechanics.buildings.Apartaments(neighbor))
                                new_apartaments -= 1
                            placed = True
                            occupied.add(neighbor)
                            
                            if placed:
                                break                  

        open_sewers = [b.position for b in buildings if isinstance(b, mechanics.buildings.Open_Sewer)] 
        while new_opened_sewers > 0:
            hex_picked = get_random_free_hex(hex_map, occupied)
            if (hex_picked not in occupied
            and all(neigh not in open_sewers for neigh in map_utils.get_neighbors(hex_picked, hex_map))
            and not any(map_utils.hex_distance(hex_picked, escape_hex) <= 2 for escape_hex in get_away_hex)):
                buildings.append(mechanics.buildings.Open_Sewer(hex_picked))
                new_opened_sewers -= 1
                occupied.add(hex_picked)
                neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                placed = False
                for neighbor in neighbors:
                    if neighbor not in occupied and new_apartaments > 0 and neighbor not in occupied_by_characters:
                        buildings.append(mechanics.buildings.Apartaments(neighbor))
                        new_apartaments -= 1
                        placed = True
                        occupied.add(neighbor)
                        break                   
        
        attempt = 0
        while new_apartaments > 0:
            hex_picked = get_random_free_hex(hex_map, occupied)
            attempt += 1
            if attempt < len(hex_map):
                if (hex_picked not in occupied and hex_picked not in occupied_by_characters
                    and not any(map_utils.hex_distance(hex_picked, escape_hex) <= 2 for escape_hex in get_away_hex)
                    and all(neigh not in occupied for neigh in map_utils.get_neighbors(hex_picked, hex_map))):
                    buildings.append(mechanics.buildings.Apartaments(hex_picked))
                    new_apartaments -= 1
                    occupied.add(hex_picked)
                    neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                    placed = False
                    for neighbor in neighbors:
                        if neighbor not in occupied and new_apartaments > 0 and neighbor not in occupied_by_characters:
                            buildings.append(mechanics.buildings.Apartaments(neighbor))
                            new_apartaments -= 1
                            placed = True
                            occupied.add(neighbor)
                            break 
            else:
                if (hex_picked not in occupied and hex_picked not in occupied_by_characters
                    and not any(map_utils.hex_distance(hex_picked, escape_hex) <= 2 for escape_hex in get_away_hex)):    
                    buildings.append(mechanics.buildings.Apartaments(hex_picked))
                    new_apartaments -= 1
                    occupied.add(hex_picked)
                    neighbors = map_utils.get_neighbors(hex_picked, hex_map)
                    placed = False
            
                    for neighbor in neighbors:
                        if neighbor not in occupied and new_apartaments > 0 and neighbor not in occupied_by_characters:
                            buildings.append(mechanics.buildings.Apartaments(neighbor))
                            new_apartaments -= 1
                            placed = True
                            occupied.add(neighbor)
                            break         