import pygame
import mechanics.map as map
import mechanics.skills as skills
class Character:
    def __init__(self, position, name, color, visible = True):
        self.position = position
        self.name = name
        self.color = color
        self.visible = visible

    def draw(self, surface, pos, color):
        size = map.size_of_hex/2
        pygame.draw.circle(surface, color, pos, size)
        pygame.draw.circle(surface, (0, 0, 0), pos, size,3)

    def action(self, player):
        raise NotImplementedError("Subclasses must implement this method")
    
class Sherlock_Holmes(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = True)

    def action(self, player):
        return skills.Sherlocks_skill(player)
    
class John_H_Watson(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = False)

    def action(self, player):
        return skills.Watsons_skill(player, self)
    
class John_Smith(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = True)

    def action(self, player):
        return skills.Smiths_skill(player)
    
class Inspector_Lestrade(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = True)

    def action(self, player):
        return skills.Lestrades_skill(player)

class Miss_Stealthy(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = False)

    def action(self, player):
        return skills.Stealhys_skill()
    
class Sergeant_Goodley(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color,  visible = False)

    def action(self, player):
        return skills.Goodleys_skill(player)

class Sir_William_Gull(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, visible = False)

    def action(self, player):
        return skills.Gulls_skill(player, self)

class Jeremy_Bert(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color,  visible = True)

    def action(self, player):
        return skills.Berts_skill(player)