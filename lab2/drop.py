from constants import *

class Drop:
    def __init__(self, position, velocity, texture):
        self.position = position
        self.velocity = velocity
        self.texture = texture

    def update(self, dt):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    def draw(self, window):
        window.blit(self.texture, self.position)

    def is_off_screen(self):
        return self.position[1] > WINDOW_HEIGHT + 40
