import random
import mechanics.map_utils as map_utils
import settings


used_names = set()
suspect_list = set()

#function to create suspect list at the beginning of the game    
def create_suspect_list():
    global suspect_list
    suspect_list.clear()
    if settings.operations:
        settings.operations += 1
    for char in settings.character_list:
        suspect_list.add(char)
        if settings.operations:
            settings.operations += 2
    return suspect_list

#function to update suspect list
def update_suspect_list():
    to_remove = set()
    
    for char in suspect_list:
        if char.visible != settings.Jack_visibility: 
            to_remove.add(char)
            if settings.operations:
                settings.operations += 2

    for char in to_remove:
        suspect_list.remove(char)
        if settings.operations:
            settings.operations += 1 + len(to_remove)
    
    return suspect_list

#function to check visibility of Jack
def is_Jack_visible():
    settings.Jack_visibility = settings.murderer.visible
    if settings.operations:
        settings.operations += 1
    return None

#function to check and change statuses of all characters on a map
def change_status():
    for char in settings.character_list:
        char.visible = False
        if settings.operations:
            settings.operations += 1

    lamp_positions = {b.position for b in settings.building_list if b.revealing}
    occupied_positions = {c.position for c in settings.character_list}
    if settings.operations:
        settings.operations += len(settings.building_list) + len(settings.character_list)

    for char in settings.character_list:
        neighbors = map_utils.get_neighbors(char.position, settings.hex_set)
        if settings.operations:
            settings.operations += 1

        for watson in (c for c in settings.character_list if c.name == "John H. Watson"):
            if char.position in getattr(watson, "lamp_path", []):
                char.visible = True
                if settings.operations:
                    settings.operations += 1
                break  

        if any(pos in lamp_positions for pos in neighbors) or \
           any(pos in occupied_positions - {char.position} for pos in neighbors):
            char.visible = True    
            if settings.operations:
                settings.operations += 1

# function to choose a murderer at the beginning of the game
def choose_murderer(characters):
    chosen = random.choice(characters)
    settings.murderer = chosen
    settings.taken_cards.append(chosen)
    if settings.operations:
        settings.operations += 3
    return chosen.name

# function to split characters equally between two groups (even and odd round)
def initialize_groups():
    chars_copy = settings.character_list.copy()
    n = len(chars_copy)
    split = n // 2  
    settings.group_a = random.sample(chars_copy, split)
    settings.group_b = [c for c in chars_copy if c not in settings.group_a]
    if settings.operations:
        settings.operations += len(settings.character_list)+ 2 +split + len(chars_copy)

#function that choose a random character to play from a given group 
def choose_random_character(characters, player):
    available_chars = [c for c in characters if c not in used_names]
    if settings.operations:
        settings.operations += len(characters)
    if not available_chars:
        used_names.clear()
        available_chars = characters.copy()
        if settings.operations:
            settings.operations += len(used_names) + len(characters)
    if not settings.random_game and player == "Jack" and settings.murderer in available_chars:
        chosen = settings.murderer
    else:
        chosen = random.choice(available_chars)
    used_names.add(chosen)
    if settings.operations:
        settings.operations += 2
    return chosen

#function that is choosing a group to play and a character, checks queues of turns
def choose_char(round):
    if round % 2 == 1 and not settings.group_a and not settings.group_b:
        used_names.clear()
        if settings.operations:
            settings.operations += len(settings.character_list)
        initialize_groups()

    if round % 2 == 1:
        available_characters = settings.group_a.copy()
    else:
        available_characters = settings.group_b.copy()

    if settings.operations:
        settings.operations += len(settings.group_a)

    if not settings.current_turn_queue:
        if round % 2 == 1:
            settings.current_turn_queue = settings.odd_round.copy()
            if settings.operations:
                settings.operations += len(settings.odd_round)
        else:
            settings.current_turn_queue = settings.even_round.copy()
            if settings.operations:
                settings.operations += len(settings.even_round)


    current_player = settings.current_turn_queue.pop(0)
    if settings.operations:
        settings.operations += 1
    

    chosen_character = choose_random_character(available_characters, current_player)


    move_info = {
        "player": current_player,
        "character" : chosen_character,
        "color": chosen_character.color
    }

    if settings.operations:
        settings.operations += 1
            
    if len(used_names) == len(settings.character_list):
        settings.group_a.clear()
        settings.group_b.clear()
        if settings.operations:
            settings.operations += len(settings.character_list)
        
    return round, move_info
