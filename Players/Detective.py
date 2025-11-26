import mechanics.deck as deck
import mechanics.map_utils as map_utils
import mechanics.actions as actions
import settings

#function that is deciding time of using skills for Detective
def Detective_activation_skill_preferences(character):
    before_movement = ["Miss Stealthy", "Sir William Gull", "Jeremy Bert"]
    if settings.operations:
        settings.operations += 1
    if character.name in before_movement:
        return 2
    return 1

#characters movement by Detective
def Detective_movement(character, random = False):
    if settings.operations:
                settings.operations += 1
    if random:
        return actions.basic_movement(character, "Detective", "random")
    else:
        if len(deck.suspect_list) == 1:
            if character != settings.murderer:
                goal = next(iter(deck.suspect_list), None)
                character.position = actions.get_to_your_goal(character, "Detective", goal.position)
                if settings.operations:
                    settings.operations += 2
                return character.position
            else:
                return actions.basic_movement(character, "Detective", "random")
        else:
            return actions.basic_movement(character, "Detective", "adaptive")
