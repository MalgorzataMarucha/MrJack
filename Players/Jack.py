import settings
import mechanics.map_utils as map_utils
import mechanics.actions as actions
import mechanics.deck as deck


def Jack_smart_movement(character):
    goal = map_utils.find_closest_escape_hex(character)[0]
    path = map_utils.find_closest_path(character, goal)

    visible_chars = {c for c in deck.suspect_list if c.visible}
    invisible_chars = {c for c in deck.suspect_list if not c.visible}
    total_path_len = len(path[0]) + len(path[1]) - 1 if len(path) > 1 else len(path[0])

    original_pos = character.position
    steps = settings.amount_of_rolls
    allow_tp = True
    if settings.operations:
        settings.operations += len(deck.suspect_list)*2 + 6
    if total_path_len <= steps:
        if settings.Jack_visibility == False:
            character.visibility = False
            character.position = actions.get_to_your_goal(character, "Jack", goal, steps)
            if settings.operations:
                settings.operations += 2
            return character.position
        else:
            return actions.hiding(character)
    
        
    if len(deck.suspect_list) > 1:
        target_visibility = len(visible_chars) > len(invisible_chars)
        if settings.operations:
                settings.operations += 2
    else:
        target_visibility = False
        if settings.operations:
                settings.operations += 1

    while steps > 0:

        target = actions.get_to_your_goal(character, "Jack", goal, steps, allow_tp)

        if not isinstance(target, tuple):
            break

        character.position = target
        if settings.operations:
            settings.operations += 1
        deck.change_status()

        if character.visible == target_visibility:
            return character.position
        
        character.position = original_pos
        if settings.operations:
            settings.operations += 1
        deck.change_status()

        if steps - 1 == 0 and len(path) != 1:
            path = map_utils.find_closest_path(character, goal, False)
            total_path_len = len(path[0]) + len(path[1]) if len(path) > 1 else len(path[0])
            steps = settings.amount_of_rolls
            allow_tp = False
            if settings.operations:
                settings.operations += 3
        else:
            steps -= 1
            if settings.operations:
                settings.operations += 1
        
    steps = settings.amount_of_rolls
    character.position = actions.get_to_your_goal(character, "Jack", goal, steps)
    if settings.operations:
        settings.operations += 2
    return character.position

def Jack_activation_skill_preferences(character):
    before_movement = ["Inspector Lestrade", "Miss Stealthy", "Sir William Gull", "Jeremy Bert"]
    if settings.operations:
        settings.operations += 1
    if character.name in before_movement:
        return 2
    return 1


def Jack_movement(character, random = False):
    if settings.operations:
        settings.operations += 1
    if random:
        return actions.basic_movement(character, "Jack", "random")
    else:
        if character == settings.murderer:
            return Jack_smart_movement(character)
        else:
            if len(deck.suspect_list) > 1:
                return actions.basic_movement(character, "Jack", "adaptive")
            else:
                return actions.basic_movement(character, "Jack", "hide")