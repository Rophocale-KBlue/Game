# start_screen.py
import random
import pygame
from config import WIDTH, HEIGHT, TITLE_COLOR, TITLE_SHADOW, DIRS
from ui import Button, get_font, draw_gradient_bg

DECOR_COLOR = (110, 150, 210)
DECOR_SIZE = 26

def _create_arrow_surface(direction, size=DECOR_SIZE, color=DECOR_COLOR):
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    half = size // 2
    shaft = pygame.Rect(cx - half, cy - 4, size, 8)
    head = [(cx + half, cy - 12), (cx + half + 14, cy), (cx + half, cy + 12)]
    pygame.draw.rect(surf, color, shaft, border_radius=3)
    pygame.draw.polygon(surf, color, head)
    angle_map = {"right": 0, "down": -90, "left": 180, "up": 90}
    return pygame.transform.rotate(surf, angle_map[direction])

_SURFACES = {d: _create_arrow_surface(d) for d in DIRS}

class _FloatingArrow:
    def __init__(self):
        self.reset(random_edge=True)

    def reset(self, random_edge=False):
        self.direction = random.choice(list(DIRS.keys()))
        self.speed = random.uniform(0.3, 1.2)
        self.alpha = random.randint(30, 80)
        self.scale = random.uniform(0.6, 1.4)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.5, 0.5)
        if random_edge:
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
        else:
            if self.direction == "right":
                self.x, self.y = -40, random.randint(0, HEIGHT)
            elif self.direction == "left":
                self.x, self.y = WIDTH + 40, random.randint(0, HEIGHT)
            elif self.direction == "down":
                self.x, self.y = random.randint(0, WIDTH), -40
            else:
                self.x, self.y = random.randint(0, WIDTH), HEIGHT + 40

    def update(self):
        dx, dy = DIRS[self.direction]
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.angle += self.rot_speed
        m = 60
        if self.x < -m or self.x > WIDTH + m or self.y < -m or self.y > HEIGHT + m:
            self.reset(random_edge=False)

    def draw(self, surface):
        base = _SURFACES[self.direction]
        w = int(base.get_width() * self.scale)
        h = int(base.get_height() * self.scale)
        img = pygame.transform.smoothscale(base, (w, h))
        img = pygame.transform.rotate(img, self.angle)
        img = img.copy()
        img.set_alpha(self.alpha)
        surface.blit(img, img.get_rect(center=(self.x, self.y)))

class StartScreen:
    def __init__(self, on_start, on_level_select, on_achievement, on_settings):
        self.background = pygame.image.load("image/start_background.png").convert()
        self.decor = [_FloatingArrow() for _ in range(18)]
        btn_w, btn_h = 200, 100
        cx = WIDTH // 2
        self.buttons = [
            Button("开始游戏", (cx, HEIGHT - 220), (btn_w, btn_h), on_start,image="image/begin_button.png"),
            Button("选择关卡", (cx, HEIGHT - 140), (btn_w, btn_h), on_level_select,image="image/level_select_button.png"),
        ]
        small_w, small_h = 150, 100
        gap = 5
        total = small_w * 2 + gap
        left_x = WIDTH // 2 - total // 2 + small_w // 2
        right_x = WIDTH // 2 + total // 2 - small_w // 2
        self.buttons.append(Button("成就", (left_x, HEIGHT - 60), (small_w, small_h), on_achievement,image="image/achievements_button.png"))
        self.buttons.append(Button("设置", (right_x, HEIGHT - 60), (small_w, small_h), on_settings,image="image/setting_button.png"))
        self.title_font = get_font(72, bold=True)
        self.sub_font = get_font(22)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, dt):
        for a in self.decor:
            a.update()
        for b in self.buttons:
            b.update(pygame.mouse.get_pos())

    def draw(self, surface):
        bg = pygame.transform.smoothscale(self.background,surface.get_size())
        surface.blit(bg, (0, 0))
        for b in self.buttons:
            b.draw(surface)