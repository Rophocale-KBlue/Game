# level_select.py
import pygame
from config import WIDTH, HEIGHT, LEVELS, TITLE_COLOR
from ui import Button, get_font, draw_gradient_bg

class LevelSelectScreen:
    def __init__(self, on_select_level, on_back):
        self.on_select_level = on_select_level
        self.buttons = []
        for i in range(len(LEVELS)):
            bx = WIDTH // 2 + (i - (len(LEVELS) - 1) / 2) * 200
            b = Button(f"第{i+1}关", (int(bx), HEIGHT // 2), (160, 120),
                       lambda idx=i: self.on_select_level(idx))
            self.buttons.append(b)
        self.back_btn = Button("返回", (WIDTH // 2, HEIGHT - 80), (160, 52), on_back)
        self.title_font = get_font(72, bold=True)
        self.small_font = get_font(18)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)
        self.back_btn.handle_event(event)

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        for b in self.buttons:
            b.update(mp)
        self.back_btn.update(mp)

    def draw(self, surface):
        draw_gradient_bg(surface)
        title = self.title_font.render("选择关卡", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 100)))
        for i, b in enumerate(self.buttons):
            b.draw(surface)
            data = LEVELS[i]
            info = self.small_font.render(
                f"{data['grid_size']}×{data['grid_size']} · {len(data['arrows'])}箭头 · {data['mistakes']}失误",
                True, (200, 210, 230))
            surface.blit(info, info.get_rect(center=(b.base_rect.centerx, b.base_rect.bottom + 24)))
        self.back_btn.draw(surface)