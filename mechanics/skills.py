import settings
from mechanics.buildings import Lantern, Lantern_Off, Police_Cordon, Open_Sewer, Closed_Sewer
import mechanics.buildings as buildings
import mechanics.deck as deck
import mechanics.map_utils as map_utils
import mechanics.actions as actions
import random

def Sherlocks_skill(player):
    char_list = settings.character_list.copy()
    random.shuffle(char_list)
    if settings.operations:
        settings.operations += len(settings.character_list) + len(char_list)
    for char in char_list:
        if settings.operations:
            settings.operations +=1 
        if char not in settings.taken_cards and char != settings.murderer:
            settings.taken_cards.append(char)
            if settings.operations:
                settings.operations +=1 
            if player == "Detective" and char in deck.suspect_list:
                deck.suspect_list.remove(char)
                if settings.operations:
                    settings.operations += len(deck.suspect_list)
            break
        else:
            continue

    return None


def Watsons_skill(player, watson):
    neighbors = map_utils.get_neighbors(watson.position, settings.hex_set)

    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}

    chosen_path = []

    if settings.operations:
        settings.operations +=  len(deck.suspect_list)*2 + 2

    match player:
        case "Jack":
            # Option 1: Murderer is visible and he is in majority (or both visible and invisible suspects has the same numbers)
            # Watson tries to light up a place where is an invisible suspect
            if settings.murderer.visible and len(visible_chars) >= len(invisible_chars):
                #print("Case 1")
                chosen_path, chosen_direction = map_utils.find_path(
                    watson, neighbors, settings.hex_set, settings.building_list,
                    lambda pos: any(c.position == pos for c in invisible_chars)
                )

            # Option 2: Murderer is invisible and is in minority (or both visible and invisible suspects has the same numbers)
            # Watson tries to make murderer visible 
            elif not settings.murderer.visible and len(visible_chars) > len(invisible_chars):
                #print("Case 2")
                chosen_path, chosen_direction = map_utils.find_path(
                    watson, neighbors, settings.hex_set, settings.building_list,
                    lambda pos: settings.murderer.position == pos
                )

                if not chosen_path:
                    #print("Case 2 - other")
                    #if it's not possible - he tries to put a light in a line without invisible suspects
                    chosen_path, chosen_direction = map_utils.find_path(
                        watson, neighbors, settings.hex_set, settings.building_list,
                        lambda pos: all(c.position != pos for c in invisible_chars)
                    )

            # Option 3: murderer is already known or there are more or equal of invisible suspects
            # Watson tries to not light up invisible characters in the suspect list
            elif len(deck.suspect_list) <= 1 or len(visible_chars) <= len(invisible_chars):
                #print("Case 3")
                chosen_path, chosen_direction = map_utils.find_path(
                    watson, neighbors, settings.hex_set, settings.building_list,
                    lambda pos: all(c.position != pos for c in invisible_chars)
                )
                
        case "Detective":
            # Option 1: Murderer is known
            # Watson tries to put a light where murderer is
            if len(deck.suspect_list) == 1:
                chosen_path, chosen_direction = map_utils.find_path(
                    watson, neighbors, settings.hex_set, settings.building_list,
                    lambda pos: settings.murderer.position == pos
                )
            # Option 2: There are more invisibile or the same amount of invisible suspects
            # Watson will try to make any invisible suspect into a visible one
            elif len(visible_chars) <= len(invisible_chars):
                chosen_path, chosen_direction = map_utils.find_path(
                    watson, neighbors, settings.hex_set, settings.building_list,
                    lambda pos: any(c.position == pos for c in invisible_chars)
                )
        case _:
            chosen_path = None
            

    # Fallback — if there is no path done
    # Watson will choose a random path to light up
    if not chosen_path:
        chosen_path, chosen_direction = map_utils.find_path(
            watson, neighbors, settings.hex_set, settings.building_list,
            fallback=True
        )

        #if chosen_path:
            #print(f" Watson nie znalazł sensownej ścieżki — używa fallbacku.")
        #else:
            #print("Brak dostępnych ścieżek do oświetlenia.")
        #    return

    # Efekt końcowy
    #print(f" Watson kieruje światło w stronę {chosen_direction}. Oświetlone hexy: {chosen_path}")

    #affected = [c.name for c in settings.character_list if c.position in chosen_path]
    #if affected:
        #print(f" Watson oświetla: {', '.join(affected)}")
    #else:
        #print(" Watson nie oświetla żadnej podejrzanej postaci.")


def Smiths_skill(player):
    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}
    neighbors = map_utils.get_neighbors(settings.murderer.position, settings.hex_set)
    goal = map_utils.find_closest_escape_hex(settings.murderer)[0]
    sorted_lanterns = map_utils.find_closest_building(goal, Lantern)
    lanterns_off = map_utils.find_closest_building(goal, Lantern_Off)
    distance_lamp = map_utils.hex_distance(sorted_lanterns[0], goal)

    on_building = None
    off_building = None
    if settings.operations:
        settings.operations += len(deck.suspect_list) *2 + 2
    match player:
        case "Jack":
            # Note: for Jack the priority is to have the closest lamp to exit turned off
            # Option 1: If there are more visible suspects and murderer is not visible
            if len(visible_chars) > len(invisible_chars) and not settings.murderer.visible:
                dist_off = map_utils.hex_distance(lanterns_off[0], goal)
                dist_jack = map_utils.hex_distance(settings.murderer.position, lanterns_off[0])
                
                # if the closest turned off lamp is next to escape point and murderer is not next to this lamp
                # or the turned off lamp is further away from escape point
                # then Smith takes turned off lamp next to murderer(if exists) and closest to exit turned on lamp exit 
                if (dist_off <= 2 and dist_jack != 1) or dist_off > 2:
                    if any(pos in lanterns_off for pos in neighbors):
                        off_building = map_utils.find_building(Lantern_Off, neighbors)
                        on_building = map_utils.find_building(Lantern, sorted_lanterns[0], multiple=False)
                        #print("CASE 1")

            # Option 2: if there are more or equal invisible suspects and murderer is visible 
            # then Smith takes turned on lamp next to murderer (if exists) and furthest to exit turned off lamp
            elif len(invisible_chars) >= len(visible_chars) and settings.murderer.visible:
                if any(pos in sorted_lanterns for pos in neighbors):
                    off_building = map_utils.find_building(Lantern_Off, lanterns_off[-1], multiple=False)
                    on_building = map_utils.find_building(Lantern, neighbors)
                    #print("CASE 2")

            else:
                # Option 3: murderer fits to the group with most of the characters
                # then Smith takes the closest turned on lamp towards exit point if it's not going to change the visibility of the murderer 
                # (except if the lamp is next to exit point) but if it's going to change the visibility of murderer then takes another closest lamp
                # similary working for turned off lamp - we take the furthest that is not going to change the visibility of murderer
                on_pos = sorted_lanterns[1] if sorted_lanterns[0] in neighbors and distance_lamp > 2 and len(sorted_lanterns) > 1 else sorted_lanterns[0]
                off_pos = lanterns_off[-2] if lanterns_off[-1] in neighbors and len(lanterns_off) > 1 else lanterns_off[-1]
                on_building = map_utils.find_building(Lantern, on_pos, multiple=False)
                off_building = map_utils.find_building(Lantern_Off, off_pos, multiple=False)
                if settings.operations:
                    settings.operations +=2
                #print("CASE 3")

        case "Detective":
            # Option 1: if murderer is known, we take the furthest lantern on from exit point and we take the closest turned off lantern
            if len(deck.suspect_list) == 1:
                on_building = map_utils.find_building(Lantern, sorted_lanterns[-1], multiple=False)
                off_building = map_utils.find_building(Lantern_Off, lanterns_off[0], multiple=False)
            else:
                # Option 2: if there are more or the same amount of invisible suspects
                # then we take a turned on lantern that is next to invisible suspect (if exists)
                # and we take turned off lantern that is not next to any visible suspect (if exists)
                if len(invisible_chars) >= len(visible_chars):
                    for pos in lanterns_off:
                        if settings.operations:
                            settings.operations +=1 
                        neighbors_lantern = map_utils.get_neighbors(pos, settings.hex_set)
                        if any(p.position in neighbors_lantern for p in invisible_chars):
                            off_building = map_utils.find_building(Lantern_Off, pos, multiple=False)
                            break
                    for pos in sorted_lanterns:
                        if settings.operations:
                            settings.operations +=1 
                        neighbors_lantern = map_utils.get_neighbors(pos, settings.hex_set)
                        if not any(p.position in neighbors_lantern for p in visible_chars):
                            on_building = map_utils.find_building(Lantern, pos, multiple=False)
                            break
        case _:
            on_building = None
            off_building = None
            if settings.operations:
                settings.operations +=2

    # if any of the lamps are not existing then we take a random lamps to switch
    if not on_building or not off_building:
        on_building = map_utils.find_building(Lantern, random.choice(sorted_lanterns), multiple=False)
        off_building = map_utils.find_building(Lantern_Off, random.choice(lanterns_off), multiple=False)

    
    on_pos = on_building.position
    off_pos = off_building.position

    index = settings.building_list.index(on_building)
    settings.building_list[index].position = off_pos

    index = settings.building_list.index(off_building)
    settings.building_list[index].position = on_pos

    if settings.operations:
        settings.operations += 4 + len(settings.building_list)*2

    if on_pos in settings.lamps_to_turn_off:
        index = settings.lamps_to_turn_off.index(on_pos)
        settings.lamps_to_turn_off[index] = off_pos
        if settings.operations:
            settings.operations +=1 + len(settings.lamps_to_turn_off)

    return None

def Lestrades_skill(player):
    cordons = map_utils.find_closest_building(settings.murderer.position, Police_Cordon)
    run_away_points = map_utils.find_closest_escape_hex(settings.murderer)
    cordon_building = None
    escape_pos = None
    if settings.operations:
        settings.operations +=2
    match player:
        case "Jack":
            # Lestrade takes the closest police_cordon and puts it on the furthest avaiable exit point
            cordon_building = map_utils.find_building(Police_Cordon, cordons[0], multiple=False)
            escape_pos = run_away_points[-1]
            if settings.operations:
                settings.operations +=1 

        case "Detective":
            # Option 1: murderer is known, then Lestrade takes the furthest from murderer police cordon and puts it
            # to the closest avaiable exit point
            if len(deck.suspect_list) == 1:
                cordon_building = map_utils.find_building(Police_Cordon, cordons[-1], multiple=False)
                escape_pos = run_away_points[0]
                if settings.operations:
                    settings.operations +=1 
        case _:
            cordon_building = None
            escape_pos = None
            if settings.operations:
                settings.operations +=2
            
    #If none of the cases fits or game is random - we choose random Cordon and random avaiable exit point
    if not cordon_building or not escape_pos:
        cordon_building = map_utils.find_building(Police_Cordon, random.choice(cordons), multiple=False)
        escape_pos = random.choice(run_away_points)
        if settings.operations:
                settings.operations +=1 


    index = settings.building_list.index(cordon_building)
    settings.building_list[index].position = escape_pos
    if settings.operations:
        settings.operations +=1 + len(settings.building_list)

    return None

def Stealhys_skill():
    # Note: Character of Miss Stealthy always has a chance to use her skill, depending on her movement she will pass through buildings or not
    impassable_builds = [b for b in settings.building_list if isinstance(b, (buildings.Apartaments, buildings.Lantern, buildings.Lantern_Off))]
    if settings.operations:
        settings.operations += len(settings.building_list)
    if not settings.already_moved:
        for building in impassable_builds:
            building.passable = True
            if settings.operations:
                settings.operations +=2
        settings.amount_of_rolls += 1
        settings.already_used_skill = False
        if settings.operations:
                settings.operations +=2
        
    else:
        for building in impassable_builds:
            building.passable = False
            if settings.operations:
                settings.operations +=2
        settings.amount_of_rolls -= 1
        if settings.operations:
            settings.operations +=1

            
    return None

def attempt_move_for_Goodleys_skill(char, Goodley, target_visibility, steps, can_be_murderer, strict):
    # function for Goodley's skill - checking if the movement of the character is possible to the conditions given
    original_visibility = settings.murderer.visible
    original_pos = char.position
    if settings.operations:
        settings.operations += 2
    target = actions.get_to_your_goal(char, "Jack", Goodley.position, steps, False, True)
    path = map_utils.find_closest_path(char, Goodley.position, teleport=False)[0]
    
    if not isinstance(target, tuple):
        char.position = original_pos
        deck.change_status()
        if settings.operations:
            settings.operations +=1 
        return None, 0  

    char.position = target
    if settings.operations:
        settings.operations +=1 
    deck.change_status()

    # if character to move cannot be a murderer and is not in suspect list and is not changing visibility of murderer after movement 
    # we can ignore visibility conditions
    if not can_be_murderer and char not in deck.suspect_list and settings.murderer.visible == original_visibility:
        target_visibility = None
        if settings.operations:
            settings.operations +=1 

    # checking visibility conditions - if fits or conditions can be skipped, movement is accepted
    if not strict or char.visible == target_visibility or target_visibility is None:
        steps_used = path.index(target)
        if settings.operations:
            settings.operations += len(path)
        return target, steps_used

    # if not accepted, we move this char to the previous position
    char.position = original_pos
    if settings.operations:
        settings.operations +=1 
    deck.change_status()
    return None, 0


def loop_for_Goodleys_skill(characters, steps_remaining, Goodley, target_visibility=None, can_be_murderer=False, strict=False, special=False):
    step_iter = range(1, steps_remaining + 1) if special else range(steps_remaining, 0, -1)
    if settings.operations:
        settings.operations += steps_remaining

    for char in characters:
        if settings.operations:
            settings.operations +=1
        if (not can_be_murderer and char == settings.murderer) or char == Goodley:
            continue

        for steps in step_iter:
            if settings.operations:
                settings.operations +=1
            if steps > steps_remaining:
                continue
            target, used = attempt_move_for_Goodleys_skill(char, Goodley, target_visibility, steps, can_be_murderer, strict)
            if target:
                steps_remaining -= used
                if settings.operations:
                    settings.operations +=1
                ##print(f"{char.name} moved to {target}, steps remaining {steps_remaining}")
                break 

        if steps_remaining <= 0:
            break

    return steps_remaining

def Goodleys_skill(player, Goodley):
    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}
    steps_remaining = settings.amount_of_rolls
    if settings.operations:
        settings.operations +=1 + len(deck.suspect_list)*2 + len(settings.character_list)

    match player:
        case "Jack":
            target_visibility = (len(visible_chars) > len(invisible_chars)) if len(deck.suspect_list) > 1 else None
            #Option 1: Goodley is not the murderer himself - Goodley will move the closest character(s) from the real murderer
            if settings.operations:
                settings.operations +=2
            if Goodley != settings.murderer:
                characters = map_utils.find_closest_character(settings.murderer)
                for strict in [True, False]:
                    if settings.operations:
                        settings.operations +=1
                    steps_remaining = loop_for_Goodleys_skill(characters, steps_remaining, Goodley, target_visibility, strict=strict)
                    if steps_remaining == 0:
                        break
            # Option 2: Goodley is the murderer himself - will try to move by the smallest amount of movements the furthest characters
            else:
                characters = map_utils.find_closest_character(Goodley, reversed=True)
                for strict in [True, False]:
                    if settings.operations:
                        settings.operations +=1
                    steps_remaining = loop_for_Goodleys_skill(characters, steps_remaining, Goodley, target_visibility, strict=strict, special=True)
                    if steps_remaining == 0:
                        break

        case "Detective":
            if len(deck.suspect_list) == 1:
                #Option 1: Goodley is not the murderer, but murderer is known - Goodley will try to move first as much as he can
                # the murderer to himself, if there are any movements left - he takes random characters to move
                if Goodley != settings.murderer:
                    target = actions.get_to_your_goal(settings.murderer, "Jack", Goodley.position, steps_remaining, False, True)
                    path = map_utils.find_closest_path(settings.murderer, Goodley.position, teleport=False)[0]
                    if isinstance(target, tuple):
                        settings.murderer.position = target
                        steps_remaining -= path.index(target)
                        if settings.operations:
                            settings.operations +=1 + len(path)
                        #print(f"{settings.murderer.name} moved to {target}, steps remaining {steps_remaining}")

                    if steps_remaining > 0:
                        steps_remaining = loop_for_Goodleys_skill(settings.character_list, steps_remaining, Goodley)
                else:
                    # Option 2: Goodley is known to be a murderer - Goodley will try to pull to himself the closest characters
                    characters = map_utils.find_closest_character(settings.murderer)
                    steps_remaining = loop_for_Goodleys_skill(characters, steps_remaining, Goodley, can_be_murderer=True)
            else:
                #Option 3: Murderer is not known - pulling the furthest characters as much as it is possible and fitting the visibility preferences
                target_visibility = len(visible_chars) <= len(invisible_chars)
                if settings.operations:
                    settings.operations +=2
                characters = map_utils.find_closest_character(Goodley, reversed=True)
                for strict in [True, False]:
                    if settings.operations:
                        settings.operations +=1
                    steps_remaining = loop_for_Goodleys_skill(characters, steps_remaining, Goodley, target_visibility, can_be_murderer=True, strict=strict)
                    if steps_remaining == 0:
                        break
        case _:
            # Random characters pulling if the game is chosen to have random movements
            characters = []
            characters = settings.character_list.copy()
            random.shuffle(characters)
            steps_remaining = loop_for_Goodleys_skill(characters, steps_remaining, Goodley, can_be_murderer=True)

            if settings.operations:
                settings.operations += len(settings.character_list) + len((characters))
    return None
    

def Gulls_skill(player, Gull):
    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}
    character_to_switch = None
    if settings.operations:
        settings.operations +=1 + len(deck.suspect_list)*2
    match player:
        case "Jack":
            goal = map_utils.find_closest_escape_hex(settings.murderer)
            target_visibility = (len(visible_chars) > len(invisible_chars)) if len(deck.suspect_list) > 1 else None
            if settings.operations:
                settings.operations +=2
            for hex in goal:
                if settings.operations:
                    settings.operations +=1
                characters = map_utils.find_closest_character(building_pos=hex)
                # Option 1: if the murderer is the closest to exit hex then there is no need of a switch that would be profitable
                if settings.murderer == characters[0]:
                    break
                else:
                    # Option 2: if the murderer is Gull and if faster will be possible to find a character closer to exit with 
                    # fitting conditions then Gull is switching with that character
                    # but if faster will be found Gull then there is no point looking further for a switch for this exit 
                    if settings.murderer == Gull:
                        for char in characters:
                            if settings.operations:
                                settings.operations +=1
                            if char == Gull:
                                break
                            else:
                                if char.visible == target_visibility or target_visibility == None:
                                    character_to_switch = char
                                    if settings.operations:
                                        settings.operations +=1
                                    break
                                else:
                                    continue    
                    # Option 3: murderer is someone else than Gull, so it's checked if Gull has proper condition related to visibility
                    #if condition exists and if he is closer to exit point than a murderer 
                    else:
                        gull_index = characters.index(Gull)
                        
                        murderer_index = characters.index(settings.murderer)
                        if settings.operations:
                            settings.operations += len(characters)*2
                        if (Gull.visible == target_visibility or target_visibility == None) and gull_index < murderer_index:
                            character_to_switch = settings.murderer
                            if settings.operations:
                                settings.operations +=1
                        
                if character_to_switch:
                    break
                
        case "Detective":
            if len(deck.suspect_list) == 1:
                goal = map_utils.find_closest_building(settings.murderer.position, Police_Cordon)
                for hex in goal:
                    if settings.operations:
                        settings.operations +=1
                    characters = map_utils.find_closest_character(building_pos=hex)
                    #Option 1: if the murderer is the closest to exit hex then there is no need of a switch that would be profitable
                    if settings.murderer == characters[0]:
                        break
                    else:
                        # Option 2: if Gull is the murderer, he can switch with first person that is the closest to the Police Cordon
                        if settings.murderer == Gull:
                            character_to_switch = characters[0]
                            if settings.operations:
                                settings.operations +=1
                        # Option 3: someone is the murderer, Gull checks who is closer to the Police Cordon
                        # if he is closer, he switches places with the murderer
                        else:
                            gull_index = characters.index(Gull)
                            murderer_index = characters.index(settings.murderer)
                            if settings.operations:
                                settings.operations += len(characters)*2
                            if gull_index < murderer_index:
                                character_to_switch = settings.murderer
                                if settings.operations:
                                    settings.operations +=1
                    
                    if character_to_switch:
                        break
        # Situation when game is chosen to be random, player chooses randomly if he wants to switch or not
        # if he wants then he is choosing a random person to switch
        case _:
            if random.choice([True, False]):
                if settings.operations:
                    settings.operations +=1
                while True:
                    character_to_switch = random.choice(settings.character_list)
                    if settings.operations:
                        settings.operations +=1
                    if character_to_switch != Gull:
                        break

    if character_to_switch and Gull:
        gull_pos = Gull.position
        switch_pos = character_to_switch.position

        Gull.position = switch_pos
        character_to_switch.position = gull_pos
        settings.already_moved = True
        deck.change_status()
        if settings.operations:
            settings.operations +=5

    return character_to_switch

def Berts_skill(player):
    goal = map_utils.find_closest_escape_hex(settings.murderer)[0]
    opened_sewers = map_utils.find_closest_building(goal, Open_Sewer)
    closed_sewers_to_goal = map_utils.find_closest_building(goal, Closed_Sewer)
    closed_sewers_to_murderer = map_utils.find_closest_building(settings.murderer.position, Closed_Sewer)

    closed_build = None
    opened_build = None
    chosen_sewer = None
    if settings.operations:
        settings.operations +=3
    match player:
        case "Jack":
            # Bert tries to take opened sewer that is not close to any of the exit points 
            # and take the closest to the murderer closed sewer
            for sewer in range(len(opened_sewers)):
                if settings.operations:
                    settings.operations +=1
                if map_utils.hex_distance(opened_sewers[sewer], goal) > settings.amount_of_rolls:
                    opened_build = map_utils.find_building(Open_Sewer, opened_sewers[sewer], False)
                    break
                else:
                    continue
                    
            closed_build = map_utils.find_building(Closed_Sewer, closed_sewers_to_murderer[0], False)

        case "Detective":
            # Option 1: if murderer is known, bert takes the closest to the exit opened sewer anf switches with the furthest
            if len(deck.suspect_list) == 1:
                opened_build = map_utils.find_building(Open_Sewer, opened_sewers[0], False)
                closed_build = map_utils.find_building(Closed_Sewer, closed_sewers_to_goal[-1], False)
            # Option 2: tries to take any opened sewer that is close to any exit point, 
            # if he finds any then he tries to take any closed 
            else:
                chosen_sewer = next((pos for pos in opened_sewers 
                    if any(map_utils.hex_distance(pos, escape_hex) < settings.amount_of_rolls for escape_hex in settings.get_out_hex)), None)
                if settings.operations:
                    settings.operations += len(settings.get_out_hex) + len(opened_sewers)
                if chosen_sewer:
                    opened_build = map_utils.find_building(Open_Sewer, chosen_sewer, False)
                    closed_build = map_utils.find_building(Closed_Sewer, random.choice(closed_sewers_to_goal), False)
        
        case _:
            opened_build = None
            closed_build = None
            if settings.operations:
                settings.operations +=2
                   
    # if nothing will be chosen/game is random then Berts takes random sewers to switch
    if not opened_build or not closed_build:
        opened_build = map_utils.find_building(Open_Sewer, random.choice(opened_sewers), False)
        closed_build = map_utils.find_building(Closed_Sewer, random.choice(closed_sewers_to_goal), False)                
                
    
    opened_pos = opened_build.position
    closed_pos = closed_build.position

    opened_build.position = closed_pos
    closed_build.position = opened_pos
    if settings.operations:
        settings.operations +=4

    return None