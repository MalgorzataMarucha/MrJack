import pygame
import mechanics.buildings as buildings
import graphics
import settings

#initializing the graphics
def init_graphics():
    global screen, background, background_base, font
    global icon_map, last_move_text, last_move_color

    pygame.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    font = pygame.font.SysFont("Arial", 20)
    last_move_text = ""
    last_move_color = (255, 255, 255)  


    screen = pygame.display.set_mode((int(screen_width * 0.85), int(screen_height * 0.85)), pygame.RESIZABLE)
    background_base = pygame.image.load("Photos/background.png")
    background = pygame.transform.scale(background_base, screen.get_size())

    icon_map = {
        buildings.Apartaments: pygame.image.load("Photos/building.jpg").convert_alpha(),
        buildings.Lantern: pygame.image.load("Photos/lantern.png").convert_alpha(),
        buildings.Lantern_Off: pygame.image.load("Photos/lantern_off.png").convert_alpha(),
        buildings.Open_Sewer: pygame.image.load("Photos/sewer_opened.png").convert_alpha(),
        buildings.Closed_Sewer: pygame.image.load("Photos/sewer_closed.png").convert_alpha(),
        buildings.Police_Cordon: pygame.image.load("Photos/cordon.jpg").convert_alpha(),
    }

def get_icon_for_building(building_obj):
    return icon_map.get(type(building_obj), None)

#drawing all elements on the screen
def draw_everything():
    global offset_x, offset_y
    graphics.screen.blit(graphics.background, (0, 0))

    positions = [hex.hex_to_pixel() for hex in settings.hex_map]
    xs = [pos[0] for pos in positions]
    ys = [pos[1] for pos in positions]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    offset_x = (graphics.screen.get_width() - (max_x - min_x)) / 2 - min_x
    offset_y = (graphics.screen.get_height() - (max_y - min_y)) / 2 - min_y

    buildings_with_icons = [
        (b, graphics.get_icon_for_building(b)) for b in settings.building_list
    ]

    for hex in settings.hex_map:
        pos = (hex.q, hex.r)
        building_tuple = next(((b, i) for (b, i) in buildings_with_icons if b.position == pos), None)

        if building_tuple:
            building_obj, icon = building_tuple
            pixel_pos = hex.hex_to_pixel()
            pixel_pos = (pixel_pos[0] + offset_x, pixel_pos[1] + offset_y)
            building_obj.draw(graphics.screen, pixel_pos, icon)
            hex.draw(graphics.screen, offset_x, offset_y, 1)
        else:
            hex.draw(graphics.screen, offset_x, offset_y, 0)

    for char in settings.character_list:
        pos = char.position
        hex = next((h for h in settings.hex_map if (h.q, h.r) == pos), None)
        if char == settings.murderer and settings.who_caught:
            continue
        if hex:
            pixel_pos = hex.hex_to_pixel()
            pixel_pos = (pixel_pos[0] + offset_x, pixel_pos[1] + offset_y)
            char.draw(graphics.screen, pixel_pos, char.color)
        
             

    for hex in settings.hex_map:
        if (hex.q, hex.r) in settings.get_out_hex:
            hex.draw(graphics.screen, offset_x, offset_y, 2)

#drawing a box with actions informations
def display_move_info(screen, font, text, text_color, background_color=(0, 0, 0, 180), padding=10):
    if not text:
        return

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(midtop=(screen.get_width() // 2, 10))

    bg_rect = pygame.Rect(
        text_rect.left - padding,
        text_rect.top - padding,
        text_rect.width + 2 * padding,
        text_rect.height + 2 * padding
    )

    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill(background_color)

    screen.blit(bg_surface, bg_rect.topleft)
    screen.blit(text_surface, text_rect)

#display box with murder information
def display_murderer_info(screen, font, murderer_name,round_number, text_color, bg_color=(0, 0, 0), padding=10, spacing=5):
    if not murderer_name:
        return

    round_text = f"Round {round_number}"
    murderer_text = f"Murderer is: {murderer_name}"

    round_surface = font.render(round_text, True, (255, 255, 255))
    murderer_surface = font.render(murderer_text, True, text_color)

    width = max(round_surface.get_width(), murderer_surface.get_width()) + 2 * padding
    height = round_surface.get_height() + spacing + murderer_surface.get_height() + 2 * padding

    bg_rect = pygame.Rect(10, 10, width, height)

    pygame.draw.rect(screen, bg_color, bg_rect, border_radius=8)

    screen.blit(round_surface, (bg_rect.left + padding, bg_rect.top + padding))
    screen.blit(murderer_surface, (bg_rect.left + padding, bg_rect.top + padding + round_surface.get_height() + spacing))


#display box with suspect list
def draw_suspect_list(screen, font, suspects, margin=20, text_color=(255,255,255), bg_color=(0, 0, 0), padding=10, spacing=5):
    if not suspects:
        return
    
    title_surface = font.render("Suspect List:", True, text_color)
    suspect_surfaces = [font.render(char.name, True, char.color) for char in suspects]
    
    max_width = max([title_surface.get_width()] + [s.get_width() for s in suspect_surfaces])
    
    total_height = title_surface.get_height() + spacing + sum(s.get_height() + spacing for s in suspect_surfaces) + padding * 2
    
    x = screen.get_width() - max_width - 2 * padding - margin
    y = margin  
    
    bg_rect = pygame.Rect(x, y, max_width + 2 * padding, total_height)
    
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    screen.blit(bg_surface, (bg_rect.x, bg_rect.y))
    
    screen.blit(title_surface, (x + padding, y + padding))
    
    offset_y = y + padding + title_surface.get_height() + spacing
    for s in suspect_surfaces:
        screen.blit(s, (x + padding, offset_y))
        offset_y += s.get_height() + spacing
