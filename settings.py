

import mechanics.map as map
import mechanics.buildings as buildings
import mechanics.characters as characters


building_list = []
character_list = []
max_rounds = 8
odd_round = []
even_round = []

get_out_hex = []

operations = 1
hex_map = []
hex_set=[]

round_number = 1
current_turn_queue = []
group_a = []
group_b = []
Watsons_lamp_path = []

murderer = None
Jack_visibility = True
ready_for_next_round = False
already_moved = False
already_used_skill = False
who_caught = False
caught = False
move_stage = 0
taken_cards = []
lamps_to_turn_off = []


amount_of_rolls = 3
number_of_things= None

def init_col_row_hex():
    return [
        [0, 8],
        [0, 8],
        [0, 6],
        [0, 5],
        [-2, 5],
        [-3, 5],
        [-3, 5],
        [-3, 5],
        [-3, 4],
        [-3, 2],
        [-4, 2],
        [-6, 2],
        [-6, 2],
    ]

col_row_hex = init_col_row_hex()
random_game = False
def init_building_list():
    return [
        buildings.Apartaments((0, 1)),
        buildings.Apartaments((0, 7)),
        buildings.Apartaments((1, 2)),
        buildings.Apartaments((1, 3)),
        buildings.Apartaments((2, 2)),
        buildings.Apartaments((3, 1)),
        buildings.Apartaments((3, 3)),
        buildings.Apartaments((5, -1)),
        buildings.Apartaments((5, 1)),
        buildings.Apartaments((5, 3)),
        buildings.Apartaments((7, 2)),
        buildings.Apartaments((7, 0)),
        buildings.Apartaments((7, -2)),
        buildings.Apartaments((9, 2)),
        buildings.Apartaments((9, 0)),
        buildings.Apartaments((10, -1)),
        buildings.Apartaments((11, -2)),
        buildings.Apartaments((11, -1)),
        buildings.Apartaments((12, -6)),
        buildings.Apartaments((12, 0)),
        buildings.Lantern((1, 5)),
        buildings.Lantern((2, 0)),
        buildings.Lantern((5, 2)),
        buildings.Lantern((7, -1)),
        buildings.Lantern((10, 1)),
        buildings.Lantern((11, -4)),
        buildings.Open_Sewer((1, 1)),
        buildings.Open_Sewer((2, 3)),
        buildings.Open_Sewer((5, -3)),
        buildings.Open_Sewer((6, 1)),
        buildings.Open_Sewer((7, 4)),
        buildings.Open_Sewer((10, -2)),
        buildings.Open_Sewer((11, 0)),
        buildings.Closed_Sewer((1, 6)),
        buildings.Closed_Sewer((11, -5)),
        buildings.Police_Cordon((1, 7)),
        buildings.Police_Cordon((11, -6)),
        buildings.Lantern_Off((5, -2)),
        buildings.Lantern_Off((7, 3))
    ]

def init_char_list():
    return [
        characters.Sherlock_Holmes((6, 2), "Sherlock Holmes", (255, 0, 0)),
        characters.John_H_Watson((8, 3), "John H. Watson", (183, 101, 19)),
        characters.John_Smith((6,-1),"John Smith", (204, 204, 0)),
        characters.Inspector_Lestrade((4, 2), "Inspector Lestrade", (0, 0, 255)),
        characters.Miss_Stealthy((0, 4), "Miss Stealthy", (0, 255, 0)),
        characters.Sergeant_Goodley((12, -3), "Sergeant Goodley", (96, 96, 96)),
        characters.Sir_William_Gull((4, -2), "Sir William Gull", (153, 0, 153)),
        characters.Jeremy_Bert((8, -1), "Jeremy Bert", (255, 153, 51))   
    ]
def reset(amount = 0):
    import mechanics.deck as deck
    global round_number, max_rounds, caught, who_caught, operations
    global already_moved, already_used_skill, ready_for_next_round
    global amount_of_rolls, move_stage, Jack_visibility, group_a, group_b
    global murderer, character_list, current_turn_queue, Watsons_lamp_path
    global get_out_hex, building_list, hex_map, taken_cards, lamps_to_turn_off
    global number_of_things, hex_map, hex_set, odd_round, even_round

    operations = 1
    deck.suspect_list.clear()
    odd_round = ["Detective", "Jack", "Jack", "Detective"]
    even_round = ["Jack", "Detective", "Detective", "Jack"]
    building_list = init_building_list()
    character_list = init_char_list()
    hex_map = map.hex_map_generator(col_row_hex, operations)
    hex_set = []

    get_out_hex = [
        (0, col_row_hex[0][0]),
        (len(col_row_hex) - 2, col_row_hex[-2][0]),
        (1, col_row_hex[1][1]-1),
        (len(col_row_hex) - 1,col_row_hex[-1][1]-1)
    ]

    
    
    

    
    
    round_number = 1
    current_turn_queue = []
    group_a = []
    group_b = []
    Watsons_lamp_path = []
    

    murderer = None
    Jack_visibility = True
    ready_for_next_round = False
    already_moved = False
    already_used_skill = False
    who_caught = False
    caught = False
    amount_of_rolls = 3
    move_stage = 0
    taken_cards = []
    lamps_to_turn_off = []

    amount_of_rolls = 3
    
    number_of_things = len(building_list) + len(character_list) + len(lamps_to_turn_off) + 17 + len(hex_map)