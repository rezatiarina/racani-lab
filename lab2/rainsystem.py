import random
import pygame
from drop import Drop
from constants import *

class RainSystem:
    def __init__(self, img):
        self.drops = []
        self.img = img

        self.spawn_margin = 300
        self.spawn_rate = 120
        self.spawn_accumulator = 0

        # osnovna i ubrzana brzina stvaranja kapljica
        self.base_spawn_rate = self.spawn_rate
        self.fast_spawn_rate = self.spawn_rate * 3

        # vertikalna osnovna i ubrzana brzina padanja
        self.base_dy = (-150, -300)
        self.fast_dy = (-300, -500)

    def update(self, dt, mouse_pos, mouse_pressed=False):
        # vjetar
        wind = (mouse_pos[0] - WINDOW_WIDTH / 2) / (WINDOW_WIDTH / 2)
        wind = max(-1, min(1, wind))
        rain_dx = wind * 120

        # odabir brzine
        if mouse_pressed:
            spawn_rate = self.fast_spawn_rate
            dy_range = self.fast_dy
        else:
            spawn_rate = self.base_spawn_rate
            dy_range = self.base_dy

        # kontinuirano emitiranje
        self.spawn_accumulator += spawn_rate * dt
        while self.spawn_accumulator >= 1:
            self.spawn_accumulator -= 1
            self.add_new_drop(rain_dx, random.uniform(*dy_range))

        # update postojećih
        for drop in self.drops[:]:
            drop.velocity[0] = rain_dx
            if mouse_pressed:
                drop.velocity[1] = max(drop.velocity[1], dy_range[0])
            drop.update(dt)
            if drop.is_off_screen():
                self.drops.remove(drop)

    def add_new_drop(self, dx, dy):
        texture = pygame.transform.scale(self.img, (6, 18))

        x = random.uniform(-self.spawn_margin, WINDOW_WIDTH + self.spawn_margin)
        y = random.uniform(500, 800)

        self.drops.append(Drop([x, y], [dx, dy], texture))

    def draw(self, window):
        for drop in self.drops:
            drop.draw(window)
