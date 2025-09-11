import pygame
import graphics
import settings
import mechanics.deck as deck
import mechanics.actions as actions
import mechanics.map_utils as map_utils
import mechanics.map_switch as map_switch
import mechanics.map as map
import time
import gc
amount = 2
if amount:
     map.size_of_hex = map.size_of_hex *1/amount
map_switch.increase_the_map(settings.col_row_hex, amount)
settings.reset(amount)
map_switch.prepare_the_map(amount, settings.building_list, settings.character_list, settings.get_out_hex)
map_switch.prepare_buildings(amount, settings.building_list, settings.character_list, settings.get_out_hex, settings.hex_map)
graphics.init_graphics()
map_utils.prepare_lanterns()
deck.choose_murderer(settings.character_list)   
deck.create_suspect_list()



last_move_time = time.time()

buildings_with_icons = [
    (b, graphics.get_icon_for_building(b)) for b in settings.building_list
]
running = True
 

while running:

    graphics.draw_everything() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            graphics.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            graphics.background = pygame.transform.scale(graphics.background_base, (event.w, event.h))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if actions.finish_of_game(settings.round_number, settings.caught) == None:
                    gc.collect()
                    if settings.move_stage == 0:
                        settings.already_moved = False
                        settings.already_used_skill = False
                        settings.round_number, move_info = deck.choose_char(settings.round_number)
                        graphics.last_move_text = f"Round {settings.round_number}: {move_info['player']} chooses {move_info['character'].name}"
                        graphics.last_move_color = move_info['color'] 
                        settings.move_stage = actions.time_to_execute_skill(move_info['player'], move_info['character'])
                    elif settings.move_stage == 1:
                        actions.execute_movement(move_info['player'], move_info['character'])
                        graphics.last_move_text = f"Round {settings.round_number}: {move_info['player']} moves with {move_info['character'].name}"
                        settings.already_moved = True
                        if settings.already_used_skill:
                            settings.move_stage = 0
                        else:
                            settings.move_stage = 2
                    else: 
                        settings.already_used_skill = True
                        actions.using_characters(move_info['player'], move_info['character'])
                        graphics.last_move_text = f"Round {settings.round_number}: {move_info['player']} uses a skill of {move_info['character'].name}"
                        if settings.already_moved:
                            settings.move_stage = 0
                        else:
                            settings.move_stage = 1
                        
                        
                    if settings.ready_for_next_round and settings.already_used_skill:
                        settings.round_number += 1 
                        deck.is_Jack_visible()
                        deck.update_suspect_list()
                        settings.ready_for_next_round = False
                else:
                    graphics.last_move_text = actions.finish_of_game(settings.round_number, settings.caught)
                    print(settings.operations)
                    graphics.last_move_color = (255, 255, 255)
                    settings.move_stage = 2

    graphics.display_move_info(graphics.screen, graphics.font, graphics.last_move_text, graphics.last_move_color)
    graphics.display_murderer_info(graphics.screen, graphics.font, settings.murderer.name, settings.round_number, settings.murderer.color)
    graphics.draw_suspect_list(graphics.screen, graphics.font, deck.suspect_list)

    pygame.display.flip()

pygame.quit()
 