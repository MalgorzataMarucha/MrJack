import pygame
import mechanics.map as map

class Character:
    def __init__(self, position, name, color, skill_before = False, skill_anytime = False, visible = True):
        self.position = position
        self.name = name
        self.color = color
        self.skill_anytime = skill_anytime
        self.visible = visible

    def draw(self, surface, pos, color):
        size = map.size_of_hex/2
        pygame.draw.circle(surface, color, pos, size)
        pygame.draw.circle(surface, (0, 0, 0), pos, size,3)

    def action(self):
        raise NotImplementedError("Subclasses must implement this method")
    
class Sherlock_Holmes(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = False, visible = True)

    def action(self):
        return "Sherlock Holmes"
    
class John_H_Watson(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = False, visible = False)
         self.lamp_path = []

    def action(self):
        return "John H. Watson"
    
class John_Smith(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = True, visible = True)

    def action(self):
        return "John Smith"
    
class Inspector_Lestrade(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = True, visible = True)

    def action(self):
        return "Inspector Lestrade"

class Miss_Stealthy(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = True, skill_anytime = True, visible = False)

    def action(self):
        return "Miss Stealthy"
    
class Sergeant_Goodley(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = True, visible = False)

    def action(self):
        return "Sergeant Goodley"

class Sir_William_Gull(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = True, skill_anytime = True, visible = False)

    def action(self):
        return "Sir William Gull"

class Jeremy_Bert(Character):
    def __init__(self, position, name, color):
         super().__init__(position, name, color, skill_before = False, skill_anytime = True, visible = True)

    def action(self):
        return "Jeremy Bert"