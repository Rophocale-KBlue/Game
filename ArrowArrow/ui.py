# ui.py
import os
import pygame
from config import (
    WIDTH, HEIGHT, BG_TOP, BG_BOTTOM, BTN_NORMAL, BTN_HOVER, BTN_TEXT,
    FONT_CANDIDATES
)

_font_cache = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key in _font_cache:
        return _font_cache[key]
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                f = pygame.font.Font(path, size)
                _font_cache[key] = f
                return f
            except Exception:
                continue
    for name in ["Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f.render("测试", True, (255, 255, 255)).get_width() > 0:
                _font_cache[key] = f
                return f
        except Exception:
            continue
    f = pygame.font.Font(None, size)
    _font_cache[key] = f
    return f

def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

class Button:
    def __init__(self, text, center, size, callback, font=None):
        self.text = text
        self.base_rect = pygame.Rect(0, 0, *size)
        self.base_rect.center = center
        self.callback = callback
        self.font = font or get_font(30, bold=True)
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.hover_scale = 1.08

    def update(self, mouse_pos):
        self.hovered = self.base_rect.collidepoint(mouse_pos)
        self.target_scale = self.hover_scale if self.hovered else 1.0
        self.scale += (self.target_scale - self.scale) * 0.2

    def draw(self, surface):
        w = int(self.base_rect.width * self.scale)
        h = int(self.base_rect.height * self.scale)
        rect = pygame.Rect(0, 0, w, h)
        rect.center = self.base_rect.center
        color = BTN_HOVER if self.hovered else BTN_NORMAL
        pygame.draw.rect(surface, color, rect, border_radius=16)
        pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=16)
        text_surf = self.font.render(self.text, True, BTN_TEXT)
        surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    def handle_event(self, event, offset=(0, 0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = (event.pos[0] - offset[0], event.pos[1] - offset[1])
            if self.base_rect.collidepoint(pos):
                self.callback()