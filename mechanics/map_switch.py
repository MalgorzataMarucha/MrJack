import random
import mechanics.buildings
import numpy as np
import mechanics.map_utils as map_utils
import mechanics.map

#function to change a basi character list depending on a number of character given 
def change_char_list(amount, character_list):
    from settings import odd_round, even_round
    if amount != 8 and amount % 2 == 0:
        if amount < 8:
            invisible_chars = [c for c in character_list if not c.visible]
            visible_chars = [c for c in character_list if c not in invisible_chars]
            to_remove_inv = random.sample(invisible_chars,int((8 - amount)/2))
            to_remove_vis = random.sample(visible_chars,int((8 - amount)/2))
            to_remove = to_remove_inv + to_remove_vis
            for char in to_remove:
                character_list.remove(char)
            how_many_per_round = int(amount/2)
            queue = odd_round[:how_many_per_round]
            odd_round.clear()
            for x in queue:
                odd_round.append(x)

            queue = even_round[:how_many_per_round]
            even_round.clear()
            for x in queue:
                even_round.append(x)
                
        elif amount > 8 and amount <=16:
            to_add = random.sample(character_list, amount-8)
            visible_chars = random.sample(to_add, int(len(to_add)/2))
            visible_pos = [(3,2),(4,3),(8,-2),(9,-1)]
            invisible_chars = [c for c in to_add if c not in visible_chars]
            invisible_pos = [(4,0),(6,-3),(8,1),(8,3)]
            for char in visible_chars:
                cls = type(char)
                pos = random.sample(visible_pos,1)
                visible_pos.remove(pos[0])
                new_char = cls((pos[0]), char.name, char.color)
                character_list.append(new_char)
            
            for char in invisible_chars:
                cls = type(char)
                pos = random.sample(invisible_pos, 1)
                invisible_pos.remove(pos[0])
                new_char = cls((pos[0]), char.name, char.color)
                character_list.append(new_char)

            how_many_per_round = int(amount/2)
            how_many_to_add = how_many_per_round-4
            odd_add = odd_round[:how_many_to_add]
            even_add = even_round[:how_many_to_add]
            for x in range(how_many_to_add):
                odd_round.append(odd_add[x])
                even_round.append(even_add[x])

 #function to increase a size of the map               
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
        
#function to choose a random hex that is not already occupied        
def get_random_free_hex(hex_map, occupied):
    free_hexes = [h for h in hex_map if (h.q, h.r) not in occupied]
    if not free_hexes:
        return None
    choice = random.choice(free_hexes)
    return (choice.q, choice.r)

#function to move basic elements of the map to the middle after map increase
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

#function to scale amount of buildings to map increase
def scale_amount_of_items(amount,buildings, type_of_item):
    from settings import init_building_list
    buildings = init_building_list()
    actual_number =  len({b.position for b in buildings if isinstance(b, type_of_item)})
    return ((1+amount/2) * actual_number - actual_number)

#function to give hexes in given distance
def get_ring(pos, distance, hex_set):
    directions = [(+1, 0), (+1, -1), (0, -1),
                  (-1, 0), (-1, +1), (0, +1)]
    results = []
    q, r = pos[0] + directions[4][0] * distance, pos[1] + directions[4][1] * distance
    for i in range(6):  
        for _ in range(distance):
            candidate = (q, r)
            if mechanics.map.Hex(q, r, -q-r) in hex_set:
                results.append(candidate)
            q += directions[i][0]
            r += directions[i][1]
    return results

#function to check if building is not influencing the environment (for example characters visibility)
def check_building(amount, new_pos, distance, type_of_build, get_away_hex):
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
            too_close_to_escape = any(
                map_utils.hex_distance(build.position, escape_hex) == distance for escape_hex in get_away_hex
            )
            too_close_to_char = any(
                map_utils.hex_distance(build.position, char.position) == 1 for char in character_list
            )
            if not too_close_to_char and not too_close_to_escape:
                to_remove = build.position
                build.position = new_pos
                return amount, to_remove
        return amount, None  


    
#function to add more buildings to the map after increase 
def prepare_buildings(amount, buildings, characters, get_away_hex, hex_map, build_to_skip):
    #preparation is needed only if the map is going to be increased
    if amount > 0:
        occupied = {b.position for b in buildings} 
        occupied_by_characters = {c.position for c in characters} 
        new_apartaments =  np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Apartaments))
        new_opened_sewers = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Open_Sewer))
        new_closed_sewers = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Closed_Sewer))
        new_lanterns_on = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Lantern))
        new_lanterns_off = np.ceil(scale_amount_of_items(amount, buildings, mechanics.buildings.Lantern_Off))

        if build_to_skip:
            if build_to_skip == "apartament":
                new_apartaments = 0
            elif build_to_skip == "sewer":
                new_closed_sewers = 0
                new_opened_sewers = 0
            elif build_to_skip == "lamp":
                new_lanterns_off = 0
                new_lanterns_on = 0
        
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
        attempt = 0
        while new_lanterns_off > 0 and attempt < len(hex_map):
            attempt += 1
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
        
        attempt = 0
        while new_closed_sewers > 0 and attempt < len(hex_map):
            attempt += 1
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
        attempt2 = 0                        
        while new_lanterns_on > 0 and attempt2 < len(hex_map):
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
                attempt2 += 1
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
        attempt = 0
        while new_opened_sewers > 0 and attempt < len(hex_map):
            attempt += 1
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
        attempt2 = 0
        while new_apartaments > 0 and attempt2 < len(hex_map):
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
                attempt2 += 1
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