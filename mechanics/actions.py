import settings
import mechanics.map_utils as map_utils
import mechanics.deck as deck
import random
import Players.Jack as Jack
import Players.Detective as Detective
from mechanics.buildings import Open_Sewer
import mechanics.skills as skills

#function to teleport between sewers
def random_sewer_teleport(player, character, remaining_moves, open_sewers, forbidden_positions):
    occupied_positions = {c.position for c in settings.character_list if c != character}
    random.shuffle(open_sewers)
    if settings.operations:
        settings.operations += len(settings.character_list) + len(open_sewers)

    for sewer in open_sewers:
        if settings.operations:
            settings.operations += 1
        if sewer in occupied_positions:
            if remaining_moves > 1 and random.choice([True, False]):
                character.position = sewer
                remaining_moves -= 1
                accessible_hexes = map_utils.get_accessible_hexes(character, player, settings.hex_map, remaining_moves, settings.building_list, forbidden_positions)
                valid_end_positions = map_utils.get_valid_end_positions(player, character, accessible_hexes, occupied_positions, forbidden_positions, settings.building_list, allow_shared_sewers=False, remaining_moves=remaining_moves)
                if settings.operations:
                    settings.operations += 2
                if valid_end_positions:
                    pos, cost = random.choice(valid_end_positions)
                    character.position = pos
                    if settings.operations:
                        settings.operations += 2
                    
                    return 0, character.position
            continue
        else:
            character.position = sewer
            remaining_moves -= 1
            if settings.operations:
                settings.operations += 2
            if remaining_moves > 0 and random.choice([True, False]):
                accessible_hexes = map_utils.get_accessible_hexes(character, player,settings.hex_map, remaining_moves, settings.building_list, forbidden_positions)
                valid_end_positions = map_utils.get_valid_end_positions(player, character, accessible_hexes, occupied_positions, forbidden_positions, settings.building_list, allow_shared_sewers=False, remaining_moves=remaining_moves)
                
                if valid_end_positions:
                    pos, cost = random.choice(valid_end_positions)
                    character.position = pos
                    if settings.operations:
                        settings.operations += 2
                    return 0, character.position
            
            return 0, character.position
    
    return remaining_moves, character.position

#function for basic movement of the characters
def basic_movement(character, player, mode):
    original_pos = character.position
    remaining_moves = settings.amount_of_rolls
    

    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}

    occupied_positions = {c.position for c in settings.character_list if c != character}
    forbidden_positions = set(settings.get_out_hex)

    accessible_hexes = map_utils.get_accessible_hexes(character, player, settings.hex_map, remaining_moves, settings.building_list, forbidden_positions)
    valid_end_positions = map_utils.get_valid_end_positions(player, character, accessible_hexes, occupied_positions, forbidden_positions, settings.building_list, allow_shared_sewers=True, remaining_moves=remaining_moves)
    open_sewers = [b.position for b in settings.building_list if isinstance(b, Open_Sewer)]
    
    if settings.operations:
        settings.operations += 2 + 2*len(deck.suspect_list) + len(settings.character_list) + len(settings.building_list) + len(forbidden_positions)
    
    if mode == "adaptive":
        target_visibility = False
        if settings.operations:
            settings.operations += 1
        if player == "Jack":
            target_visibility = len(visible_chars) > len(invisible_chars)
            if settings.operations:
                settings.operations += 2
        else: 
            target_visibility = len(visible_chars) <= len(invisible_chars)
            if settings.operations:
                settings.operations += 2

    elif mode == "hide":
        target_visibility = False
        if settings.operations:
            settings.operations += 1
        

    #possibility to teleport
    if character.position in open_sewers and remaining_moves >= 1:
        if random.choice([True, False]):
            remaining_moves, new_pos = random_sewer_teleport(player, character, remaining_moves, open_sewers, forbidden_positions)
            deck.change_status()
            if settings.operations:
                settings.operations += 1
            if mode != "random":
                if character.visible == target_visibility:
                    return new_pos
                else:
                    character.position = original_pos
                    deck.change_status()
                    remaining_moves = settings.amount_of_rolls
                    if settings.operations:
                        settings.operations += 2

    if remaining_moves <= 0:
        return character.position
    
    accessible_hexes = map_utils.get_accessible_hexes(character, player, settings.hex_map, remaining_moves, settings.building_list, forbidden_positions)
    valid_end_positions = map_utils.get_valid_end_positions(player, character, accessible_hexes, occupied_positions, forbidden_positions, settings.building_list, allow_shared_sewers=True, remaining_moves=remaining_moves)

    random.shuffle(valid_end_positions)
    if settings.operations:
        settings.operations += len(valid_end_positions)
    #looking for avaiable position
    for pos, cost in valid_end_positions:
        use_teleport = random.choice([True, False])
        if settings.operations:
            settings.operations += 2
        if pos in open_sewers and use_teleport:
            remaining_moves -= cost
            remaining_moves, new_pos = random_sewer_teleport(player, character, remaining_moves, open_sewers, forbidden_positions)
            character.position = new_pos
            deck.change_status()
            if settings.operations:
                settings.operations += 2
            if mode != "random":
                if character.visible == target_visibility:
                    return new_pos
                else:
                    character.position = original_pos
                    deck.change_status()
                    remaining_moves = settings.amount_of_rolls
                    if settings.operations:
                        settings.operations += 2
                    continue
            return new_pos  
        else:
            if pos in occupied_positions:
                if player == "Detective" and len(deck.suspect_list) == 1 and pos == settings.murderer.position and character != settings.murderer:
                    character.position = pos
                    settings.caught = True
                    settings.who_caught = character
                    deck.change_status()
                    if settings.operations:
                        settings.operations += 3
                    return character.position
                else:
                    continue

            character.position = pos
            deck.change_status()
            if settings.operations:
                settings.operations += 1
            if mode != "random":
                if character.visible == target_visibility:
                    return pos
                else:
                    character.position = original_pos
                    deck.change_status()
                    remaining_moves = settings.amount_of_rolls
                    if settings.operations:
                        settings.operations += 2
                    continue
            return character.position
    
    deck.change_status()
    return character.position

# hiding function for Jack if he cannot get to the goal because of his visibility
def hiding(character):
    original_pos = character.position
    max_steps = settings.amount_of_rolls

    occupied_positions = {c.position for c in settings.character_list if c != character}
    forbidden_positions = set(settings.get_out_hex)
    if settings.operations:
        settings.operations += 2 + len(settings.character_list) + len(forbidden_positions)

    for steps in range(1, max_steps + 1):
        accessible_hexes = map_utils.get_accessible_hexes(character, "Jack",settings.hex_map, steps, settings.building_list, forbidden_positions)
        valid_positions = map_utils.get_valid_end_positions("Jack", character, accessible_hexes, occupied_positions, forbidden_positions, settings.building_list, allow_shared_sewers=True, remaining_moves=steps)

        random.shuffle(valid_positions)
        if settings.operations:
            settings.operations += len(valid_positions)
        for pos, cost in valid_positions:
            character.position = pos
            if settings.operations:
                settings.operations += 2
            deck.change_status()

            if not character.visible:
                return pos  


            character.position = original_pos
            if settings.operations:
                settings.operations += 1
            deck.change_status()

    escape_hexes = map_utils.find_closest_escape_hex(character)
    if len(escape_hexes) > 1:
        second_goal = escape_hexes[1]
        steps = settings.amount_of_rolls
        if settings.operations:
            settings.operations += 2

        while steps > 0:
            target = get_to_your_goal(character, "Jack", second_goal, steps)

            if not isinstance(target, tuple):
                break

            character.position = target
            if settings.operations:
                settings.operations += 1
            deck.change_status()

            if not character.visible:
                return target

            character.position = original_pos
            deck.change_status()
            steps -= 1
            if settings.operations:
                settings.operations += 2

    return basic_movement(character, "Jack", "adaptive")

# function that makes character go to the exact goal 
def get_to_your_goal(character, player, goal, steps=None, teleport = True, goodley_skill = False):
    path = map_utils.find_closest_path(character, goal, teleport)
    occupied_positions = {c.position for c in settings.character_list if c != character}
    cant_stay_on_positions = {b.position for b in settings.building_list if not b.can_stay_on}
    if settings.operations:
        settings.operations += len(settings.character_list) + len(settings.building_list)

    if steps is None:
        steps = settings.amount_of_rolls
        if settings.operations:
            settings.operations += 1
     
    if path[0]:
        #checking if path is made of teleports or not (equal 1 means path without teleport)
        if len(path) == 1:
            while steps > 0:
                if len(path[0]) - 1 >= steps:
                    target_pos = path[0][steps]
                    if settings.operations:
                        settings.operations += 1
                    if target_pos not in occupied_positions and target_pos not in cant_stay_on_positions:
                        if character == settings.murderer and settings.Jack_visibility and target_pos in settings.get_out_hex:
                            steps -= 1
                            if settings.operations:
                                settings.operations += 1
                            continue
                        return target_pos
                    else:
                        if player == "Detective" and settings.murderer.position == target_pos:
                            settings.caught = True
                            settings.who_caught = character
                            if settings.operations:
                                settings.operations += 1
                            return target_pos
                steps -= 1
                if settings.operations:
                    settings.operations += 1
        else:
            while steps > 0:
                if steps >= len(path[0]):
                    #checking if sewer to which character wants to teleport is taken
                    if path[1][0] in occupied_positions and (steps - len(path[0]) <= 0):
                        if player == "Detective" and (steps - len(path[0]) == 0) and settings.murderer.position == path[1][0]:
                            target_pos = path[1][0]
                            settings.caught = True
                            settings.who_caught = character
                            if settings.operations:
                                settings.operations += 3
                            return target_pos
                        steps -= 1
                        if settings.operations:
                            settings.operations += 2
                        continue
                    else:
                        index = steps - len(path[0])
                        if settings.operations:
                            settings.operations += 1
                        if index < len(path[1]):
                            target_pos = path[1][index]
                            if settings.operations:
                                settings.operations += 1
                            if target_pos not in occupied_positions and target_pos not in cant_stay_on_positions:
                                if character == settings.murderer and settings.Jack_visibility and target_pos in settings.get_out_hex:
                                    steps -= 1
                                    if settings.operations:
                                        settings.operations += 1
                                    continue
                                return target_pos
                            else:
                                if player == "Detective" and settings.murderer.position == target_pos:
                                    settings.caught = True
                                    settings.who_caught = character
                                    if settings.operations:
                                        settings.operations += 2
                                    return target_pos
                        steps -= 1
                        if settings.operations:
                            settings.operations += 1
                        continue
                else:
                    target_pos = path[0][steps]
                    if settings.operations:
                        settings.operations += 1
                    if target_pos not in occupied_positions and target_pos not in cant_stay_on_positions:
                        if character == settings.murderer and settings.Jack_visibility and target_pos in settings.get_out_hex:
                            steps -= 1
                            if settings.operations:
                                settings.operations += 1
                            continue
                        return target_pos
                    else:
                        if player == "Detective" and settings.murderer.position == target_pos:
                            settings.caught = True
                            settings.who_caught = character
                            if settings.operations:
                                settings.operations += 2
                            return target_pos
                steps -= 1
                if settings.operations:
                    settings.operations += 1
    if goodley_skill:
        return None
    
    return basic_movement(character, player, "adaptive")

#usage of skills depending on character and mode
def using_characters(player, character, random = False):
    if random:
        if character.name != "Sherlock Holmes":
            player = None
            if settings.operations:
                settings.operations += 1
    match character.name:
        case "Sherlock Holmes":
            skills.Sherlocks_skill(player)
        case "John H. Watson":
            skills.Watsons_skill(player, character)
        case "John Smith":
            skills.Smiths_skill(player)
        case "Inspector Lestrade":
            skills.Lestrades_skill(player)
        case "Miss Stealthy":
            skills.Stealhys_skill()
        case "Sergeant Goodley":
            skills.Goodleys_skill(player, character)
        case "Sir William Gull":
            skills.Gulls_skill(player, character)
        case "Jeremy Bert":
            skills.Berts_skill(player)

    deck.change_status()
        
    return None

#execution skill preferences
def time_to_execute_skill(player, character):
    if player == "Jack":
        return Jack.Jack_activation_skill_preferences(character)
    else:
        return Detective.Detective_activation_skill_preferences(character)
        
#function to execute the movement depending on a player
def execute_movement(player, character, random = False):
    if player == "Jack":
        Jack.Jack_movement(character, random)
    else:     
        Detective.Detective_movement(character, random)
    
    deck.change_status()

    if not settings.current_turn_queue:
        settings.ready_for_next_round = True
        if settings.operations:
            settings.operations += 1
        map_utils.lanterns_off(settings.round_number)
        deck.change_status()

    return None


#function that check if game finished in any way
def finish_of_game(round, caught):
    if caught:
        return "Detective caught Jack. Detective wins!"
    elif settings.murderer.position in settings.get_out_hex:
        return "Jack managed to run away. Jack wins!"
    elif round > settings.max_rounds:
        return "Detective didn't manage to catch Jack in time. Jack wins!"
    
    if settings.operations:
        settings.operations += 1
    return None







