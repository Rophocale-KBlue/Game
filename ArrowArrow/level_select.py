# level_select.py
import pygame
from config import WIDTH, HEIGHT, LEVELS, TITLE_COLOR
from ui import Button, get_font, draw_gradient_bg

class LevelSelectScreen:
    def __init__(self, on_select_level, on_back):
        self.on_select_level = on_select_level
        self.buttons = []
        cols = 3  # 每行三个按钮
        spacing_x = 150  # 横向间距
        spacing_y = 130  # 两行之间距离
        start_x = WIDTH // 2 - spacing_x
        start_y = 240
        for i in range(len(LEVELS)):
            row = i // cols
            col = i % cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            b = Button(
                f"{i + 1}",
                (x, y),
                (60, 60),
                lambda idx=i: self.on_select_level(idx)
            )
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
            time_text = ""
            if data.get("time_limit"):
                minutes = data["time_limit"] // 60
                seconds = data["time_limit"] % 60
                time_text = f" · 时间{minutes:02d}:{seconds:02d}"
            #info = self.small_font.render(f"{data['grid_size']}×{data['grid_size']}  " f"{data['arrow_count']}箭头 " f"{data['mistakes']}失误"f"{time_text}",True,(200, 210, 230))
            #surface.blit(info, info.get_rect(center=(b.base_rect.centerx, b.base_rect.bottom + 24)))
        self.back_btn.draw(surface)