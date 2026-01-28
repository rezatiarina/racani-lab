import pygame
import sys
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List

pygame.init()

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60
GRAVITY = 0.5


class Shape(Enum):
    SQUARE = 1
    CIRCLE = 2
    TRIANGLE = 3

@dataclass
class ShapeProperties:
    speed: float
    jump_power: float
    size: int
    color: Tuple[int, int, int]

SHAPE_PROPS = {
    Shape.SQUARE: ShapeProperties(6, 13, 28, (90, 190, 255)),
    Shape.CIRCLE: ShapeProperties(8.5, 10, 22, (255, 120, 120)),
    Shape.TRIANGLE: ShapeProperties(4.5, 18, 34, (120, 255, 150)),
}


class Particle:
    def __init__(self, pos, vel, radius, color, life):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.radius = radius
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.vy += 0.3
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, screen, cam_x):
        alpha = int(255 * (self.life / self.max_life))
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (self.radius, self.radius), self.radius)
        screen.blit(surf, (self.x - cam_x - self.radius, self.y - self.radius))


class Platform:
    def __init__(self, x, y, w, h, color=(120, 120, 120)):
        self.rect = pygame.Rect(x, y, w, h, border_radius=10)
        self.color = color
        self.delta_x = 0
        self.delta_y = 0

    def update(self):
        self.delta_x = 0
        self.delta_y = 0

    def draw(self, screen, cam_x, tile_surface):
        draw_rect = self.rect.move(-cam_x, 0)
        
        tile_w = tile_surface.get_width()
        tile_h = tile_surface.get_height()
        
        for x in range(0, self.rect.width, tile_w):
            for y in range(0, self.rect.height, tile_h):
                area = pygame.Rect(0, 0, min(tile_w, self.rect.width - x), min(tile_h, self.rect.height - y))
                screen.blit(tile_surface, (draw_rect.x + x, draw_rect.y + y), area)

        pygame.draw.rect(screen, (50, 50, 50), draw_rect, 2)


class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, axis="x", amp=120, speed=0.02):
        super().__init__(x, y, w, h, (170, 140, 90))
        self.base_x = x
        self.base_y = y
        self.axis = axis
        self.amp = amp
        self.speed = speed
        self.t = 0

    def update(self):
        old_x, old_y = self.rect.x, self.rect.y
        self.t += self.speed
        if self.axis == "x":
            self.rect.x = self.base_x + math.sin(self.t) * self.amp
        else:
            self.rect.y = self.base_y + math.sin(self.t) * self.amp
        
        self.delta_x = self.rect.x - old_x
        self.delta_y = self.rect.y - old_y


class Star:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.collected = False
        self.angle = 0

    def draw(self, screen, cam_x, star_surface): 
        if not self.collected:
            self.angle += 0.05
            # floating effect
            offset_y = math.sin(self.angle * 2) * 8 
            
            # rotation effect
            rotated_star = pygame.transform.rotate(star_surface, self.angle * 50)
            rect = rotated_star.get_rect(center=(self.rect.centerx - cam_x, self.rect.centery + offset_y))
            
            screen.blit(rotated_star, rect.topleft)


class Spike:
    def __init__(self, x, y, width=40, height=30, flipped=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 50, 50)
        self.flipped = flipped

    def draw(self, screen, cam_x):
        r = self.rect.move(-cam_x, 0)
        
        if self.flipped:
            points = [
                (r.left, r.top),
                (r.right, r.top),
                (r.centerx, r.bottom)
            ]
        else:
            points = [
                (r.left, r.bottom),
                (r.centerx, r.top),
                (r.right, r.bottom)
            ]
            
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (200, 0, 0), points, 2)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0

        self.shape = Shape.SQUARE
        self.target_shape = self.shape
        self.morph_t = 1.0
        self.morph_speed = 0.12

        self.on_ground = False
        self.riding_platform = None
        self.particles: List[Particle] = []

    @property
    def props(self):
        return SHAPE_PROPS[self.shape]

    def change_shape(self, new_shape):
        if new_shape != self.target_shape:
            self.target_shape = new_shape
            self.morph_t = 0

    def spawn_jump_particles(self):
        for i in range(12):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-6, -2)
            self.particles.append(Particle((self.x, self.y + self.props.size), (vx, vy), 4, self.props.color, 30))

    def get_rect(self):
        size = self.props.size
        return pygame.Rect(self.x - size, self.y - size, size * 2, size * 2)

    def update(self, platforms):
        # morphing
        if self.morph_t < 1:
            self.morph_t += self.morph_speed
            if self.morph_t >= 1: self.shape = self.target_shape

        # sync with moving platforms
        if self.on_ground and self.riding_platform:
            self.x += self.riding_platform.delta_x * 2
            self.y = self.riding_platform.rect.top - self.props.size
            self.vel_y = 0 

        # input and gravity
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.vel_x = -self.props.speed
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vel_x = self.props.speed

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = -self.props.jump_power
            self.on_ground = False
            self.riding_platform = None
            self.spawn_jump_particles()

        self.vel_y += GRAVITY

        # vertical resokution with squish check
        self.y += self.vel_y
        self.on_ground = False
        self.riding_platform = None
        
        p_rect = self.get_rect()
        for p in platforms:
            if p_rect.colliderect(p.rect):
                if self.vel_y >= 0: # landing/falling
                    test_rect = pygame.Rect(p_rect.x, p.rect.top - (self.props.size * 2), p_rect.width, p_rect.height)
                    is_squished = any(test_rect.colliderect(other.rect) for other in platforms if other != p)
                    
                    if is_squished:
                        # instead of teleporting UP, push LEFT
                        self.x -= (self.props.size * 2)
                        # keep the Y where it was or stop it
                        self.vel_y = 0
                    else:
                        self.y = p.rect.top - self.props.size
                        self.vel_y = 0
                        self.on_ground = True
                        self.riding_platform = p
                        
                elif self.vel_y < 0: # hitting head
                    self.y = p.rect.bottom + self.props.size
                    self.vel_y = 0
                p_rect = self.get_rect()

        # horizontal resolution
        self.x += self.vel_x
        p_rect = self.get_rect()
        for p in platforms:
            if p_rect.colliderect(p.rect):
                # ignore floor contact
                if p_rect.bottom > p.rect.top + 3 and p_rect.top < p.rect.bottom - 3:
                    if self.vel_x >= 0: # moving right or being pushed right
                        self.x = p.rect.left - self.props.size
                    elif self.vel_x < 0: # moving Left
                        self.x = p.rect.right + self.props.size
                    p_rect = self.get_rect()

        # particles
        for part in self.particles[:]:
            part.update()
            if part.life <= 0: self.particles.remove(part)

        return self.y <= SCREEN_HEIGHT + 400

    def draw(self, screen, cam_x, images):
        # particles
        for p in self.particles: 
            p.draw(screen, cam_x)

        # current size
        t = self.morph_t * self.morph_t * (3 - 2 * self.morph_t)
        size = int(SHAPE_PROPS[self.shape].size * (1 - t) + SHAPE_PROPS[self.target_shape].size * t)
        
        px, py = int(self.x - cam_x), int(self.y)

        # drawing
        current_raw_img = images[self.target_shape]
        scaled_img = pygame.transform.smoothscale(current_raw_img, (size * 2, size * 2))
        screen.blit(scaled_img, (px - size, py - size))

        # eyes
        eye_size = max(2, size // 5)
        eye_dist = size // 2.5
        
        # look_offset
        look_offset = 0
        if self.vel_x > 0: look_offset = size // 6
        elif self.vel_x < 0: look_offset = -size // 6
        y_offset = -size // 5

        for side in [-1, 1]:
            ex = px + (side * eye_dist) + look_offset
            ey = py + y_offset
            
            pygame.draw.circle(screen, (255, 255, 255), (int(ex), int(ey)), eye_size) # white part
            pygame.draw.circle(screen, (0, 0, 0), (int(ex + look_offset/2), int(ey)), eye_size // 2) # black part


class Level:
    def __init__(self, platforms, finish_rect, start_pos, star_positions, spikes=None):
        self.platforms = platforms
        self.finish_rect = finish_rect
        self.start_pos = start_pos
        self.star_positions = star_positions
        self.stars = []
        self.spikes = spikes if spikes is not None else []

def get_levels():
    # PLATFORM - (x, y, w, h)

    # LEVEL 1
    l1_platforms = [
        Platform(0, 600, 1500, 80),
        Platform(600, 350, 200, 20), 
        Platform(1600, -60, 40, 520),
        Platform(1600, 510, 40, 200),
        Platform(1750, 600, 1000, 80),
    ]
    l1_star_pos = [(685, 300), (1150, 400), (2000, 450)]
    l1 = Level(l1_platforms, pygame.Rect(2600, 490, 90, 110), (100, 520), l1_star_pos)

    # LEVEL 2
    l2_platforms = [
        Platform(0, 600, 500, 50),
        Platform(600, 0, 40, 540), 
        Platform(600, 590, 150, 50),
        MovingPlatform(850, 540, 150, 20, "y", 150, 0.04), 
        Platform(1000, 350, 200, 20),
        Platform(1300, 500, 200, 20),
        Platform(1300, 200, 200, 20),
        MovingPlatform(1600, 400, 100, 20, "x", 100, 0.04),
        Platform(1900, 10, 40, 450),
        Platform(1900, 510, 40, 150),
        Platform(2050, 550, 40, 120),
        Platform(2200, 600, 600, 50),
    ]
    l2_star_pos = [(670, 500), (900, 100), (1350, 450), (1350, 150), (2150, 400)]
    l2 = Level(l2_platforms, pygame.Rect(2500, 490, 80, 110), (50, 520), l2_star_pos)

    # LEVEL 3
    l3_platforms = [
        Platform(0, 600, 1000, 50),
        MovingPlatform(1050, 400, 200, 20, "y", 150, 0.04),
        Platform(1400, 600, 600, 50),
        Platform(1400, 250, 600, 20),
        Platform(2200, 450, 200, 20),
        Platform(2500, 300, 200, 20),
        Platform(2800, 600, 600, 50),
    ]

    l3_spikes = [
        Spike(400, 560, 150, 40), 
        Spike(1550, 500, 60, 100),
        Spike(1800, 500, 60, 100),
        Spike(1650, 270, 60, 30, True),
        Spike(2810, 500, 60, 100), 
    ]

    l3_star_pos = [(470, 250), (1150, 150), (1600, 50), (1900, 400), (2600, 250)]
    l3 = Level(l3_platforms, pygame.Rect(3100, 490, 80, 110), (50, 520), l3_star_pos, l3_spikes)

    return [l1, l2, l3]


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SHAPE SHIFTER")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("lab3/Bad Coma.ttf", 64)
        self.stars_font = pygame.font.Font("lab3/Bad Coma.ttf", 48)
        self.title_font = pygame.font.Font("lab3/Bad Coma.ttf", 100)
        self.small_font = pygame.font.Font("lab3/ZenDots-Regular.ttf", 24)
        
        self.levels = get_levels()
        self.current_level_idx = 0
        self.state = "MENU"
        self.reset_level()
        self.collected_count = 0
        self.fade_alpha = 255
        self.tile_image = pygame.image.load("lab3/platform.png").convert()
        self.star_image = pygame.image.load("lab3/star.png").convert_alpha()
        self.star_image = pygame.transform.scale(self.star_image, (40, 40))
        self.door_image = pygame.image.load("lab3/door.png").convert_alpha()
        self.door_image = pygame.transform.scale(self.door_image, (90, 110))

        self.background_orig = pygame.image.load("lab3/background.jpg").convert()
        self.background = pygame.transform.scale(self.background_orig, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.player_imgs = {
            Shape.SQUARE: pygame.image.load("lab3/square.png").convert_alpha(),
            Shape.CIRCLE: pygame.image.load("lab3/circle.png").convert_alpha(),
            Shape.TRIANGLE: pygame.image.load("lab3/triangle.png").convert_alpha()
        }

    def draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render("SHAPE SHIFTER", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        instructions = [
            "Instructions:",
            "- Use 1, 2, 3 to Change Shape",
            "- SPACE to Jump, Arrow keys to Move",
            "- Collect Stars and reach the Golden Portal",
            "- Avoid Red Spikes!",
            "",
            "Press ENTER to Start"
        ]
        
        for i, line in enumerate(instructions):
            color = (200, 200, 200) if "ENTER" not in line else (100, 255, 100)
            text_surf = self.small_font.render(line, True, color)
            self.screen.blit(text_surf, (SCREEN_WIDTH//2 - text_surf.get_width()//2, 280 + i * 40))

    def reset_level(self):
        lvl = self.levels[self.current_level_idx]
        self.player = Player(lvl.start_pos[0], lvl.start_pos[1])
        lvl.stars = [Star(pos[0], pos[1]) for pos in lvl.star_positions]
        self.collected_count = 0 
        self.cam_x = 0
        self.fade_alpha = 255

    def run(self):
        while True:
            self.clock.tick(FPS)

            if self.fade_alpha > 0:
                self.fade_alpha -= 5
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # MENU LOGIC
                if self.state == "MENU":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.current_level_idx = 0
                            self.reset_level()
                            self.state = "PLAYING"
                
                # PLAY LOGIC
                elif self.state == "PLAYING":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1: self.player.change_shape(Shape.SQUARE)
                        if event.key == pygame.K_2: self.player.change_shape(Shape.CIRCLE)
                        if event.key == pygame.K_3: self.player.change_shape(Shape.TRIANGLE)
                
                # WIN LOGIC
                elif self.state == "WON":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            if self.current_level_idx < len(self.levels) - 1:
                                self.current_level_idx += 1
                                self.reset_level()
                                self.state = "PLAYING"
                            else:
                                self.state = "MENU"

            # UPDATES
            if self.state == "PLAYING":
                lvl = self.levels[self.current_level_idx]
                for p in lvl.platforms: p.update()
                
                alive = self.player.update(lvl.platforms)
                if not alive: self.reset_level()

                target_cam = self.player.x - SCREEN_WIDTH // 3
                self.cam_x += (target_cam - self.cam_x) * 0.1

                p_rect = self.player.get_rect()
                for s in lvl.spikes:
                    if p_rect.colliderect(s.rect):
                        self.reset_level()
                        break

                if self.player.get_rect().colliderect(lvl.finish_rect):
                    self.state = "WON"
                    self.final_score = f"{self.collected_count} / {len(lvl.stars)}"

            # DRAW
            if self.state == "MENU":
                self.draw_menu()
            else:
                # PLAYING and WON states
                self.screen.blit(self.background, (0, 0))
                lvl = self.levels[self.current_level_idx]

                for s in lvl.spikes: s.draw(self.screen, self.cam_x)
                for p in lvl.platforms: p.draw(self.screen, self.cam_x, self.tile_image)
                
                f_draw_pos = (lvl.finish_rect.x - self.cam_x, lvl.finish_rect.y)
                self.screen.blit(self.door_image, f_draw_pos)

                self.player.draw(self.screen, self.cam_x, self.player_imgs)

                # stars drawing
                for star in lvl.stars:
                    if not star.collected and self.player.get_rect().colliderect(star.rect):
                        star.collected = True
                        self.collected_count += 1
                        for i in range(15):
                            vel = (random.uniform(-4, 4), random.uniform(-4, 4))
                            pos = (star.rect.centerx, star.rect.centery)
                            self.player.particles.append(Particle(pos, vel, random.randint(3, 6), (255, 215, 0), 30))
                    star.draw(self.screen, self.cam_x, self.star_image)

                # UI
                info = self.small_font.render(f"Level {self.current_level_idx + 1}", True, (200, 200, 200))
                self.screen.blit(info, (20, 20))

                if self.state == "WON":
                    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 180))
                    self.screen.blit(overlay, (0,0))
                    win_txt = self.font.render("LEVEL COMPLETE!", True, (100, 255, 100))
                    score_txt = self.stars_font.render(f"STARS: {self.final_score}", True, (255, 215, 0))
                    prompt = self.small_font.render("Press SPACE for Next Level", True, (255, 255, 255))
                    self.screen.blit(win_txt, (SCREEN_WIDTH//2 - win_txt.get_width()//2, 250))
                    self.screen.blit(score_txt, (SCREEN_WIDTH//2 - score_txt.get_width()//2, 310))
                    self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, 380))
            
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(self.fade_alpha) 
            self.screen.blit(fade_surf, (0,0))

            pygame.display.flip()

if __name__ == "__main__":
    Game().run()