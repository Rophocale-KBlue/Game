# achievements.py
import json
import os
import pygame
from config import WIDTH, HEIGHT, TITLE_COLOR, ACHIEVEMENTS
from ui import Button, get_font, draw_gradient_bg

SAVE_FILE = "achievements.json"

DEFAULT_PROGRESS = {
    "cleared_levels": [],
    "total_arrows_flew": 0,
    "unlocked": [],
}

# ============================================================
# 数据管理
# ============================================================
class AchievementManager:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.progress = {
            "cleared_levels": [],
            "total_arrows_flew": 0,
            "unlocked": [],
        }
        self.newly_unlocked = []
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.progress["cleared_levels"] = list(data.get("cleared_levels", []))
                self.progress["total_arrows_flew"] = int(data.get("total_arrows_flew", 0))
                self.progress["unlocked"] = list(data.get("unlocked", []))
            except Exception as e:
                print(f"成就存档读取失败: {e}")

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"成就存档写入失败: {e}")

    def on_level_cleared(self, level_index):
        if level_index not in self.progress["cleared_levels"]:
            self.progress["cleared_levels"].append(level_index)
        self._check_all()
        self.save()

    def on_arrow_flew(self, count=1):
        self.progress["total_arrows_flew"] += count
        self._check_all()
        self.save()

    def _check_all(self):
        for ach in ACHIEVEMENTS:
            if ach["id"] in self.progress["unlocked"]:
                continue
            try:
                if ach["check"](self.progress):
                    self.progress["unlocked"].append(ach["id"])
                    self.newly_unlocked.append(ach)
            except Exception as e:
                print(f"成就检查失败 {ach['id']}: {e}")

    def is_unlocked(self, ach_id):
        return ach_id in self.progress["unlocked"]

    def consume_newly_unlocked(self):
        items = self.newly_unlocked[:]
        self.newly_unlocked.clear()
        return items

    def reset_all(self):
        self.progress = {
            "cleared_levels": [],
            "total_arrows_flew": 0,
            "unlocked": [],
        }
        self.save()

# ============================================================
# 成就界面
# ============================================================
class AchievementScreen:
    def __init__(self, on_back, achievement_manager):
        self.on_back = on_back
        self.ach = achievement_manager
        self.back_btn = Button("返回", (WIDTH // 2, HEIGHT - 70), (160, 52), on_back)
        self.reset_btn = Button("重置进度", (WIDTH // 2 + 200, HEIGHT - 70), (160, 52), self._on_reset)
        self.title_font = get_font(56, bold=True)
        self.item_font = get_font(22)
        self.desc_font = get_font(16)

    def _on_reset(self):
        self.ach.reset_all()

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.reset_btn.handle_event(event)

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        self.back_btn.update(mp)
        self.reset_btn.update(mp)

    def draw(self, surface):
        draw_gradient_bg(surface)
        title = self.title_font.render("成就", True, TITLE_COLOR)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 70)))

        total = len(ACHIEVEMENTS)
        done = sum(1 for a in ACHIEVEMENTS if self.ach.is_unlocked(a["id"]))
        prog = self.item_font.render(f"已解锁 {done} / {total}", True, (200, 210, 230))
        surface.blit(prog, prog.get_rect(center=(WIDTH // 2, 120)))

        start_y = 175
        row_h = 68
        for i, ach in enumerate(ACHIEVEMENTS):
            unlocked = self.ach.is_unlocked(ach["id"])
            self._draw_item(surface, ach, unlocked, start_y + i * row_h)

        self.back_btn.draw(surface)
        self.reset_btn.draw(surface)

    def _draw_item(self, surface, ach, unlocked, y):
        w, h = 560, 56
        rect = pygame.Rect(WIDTH // 2 - w // 2, y, w, h)
        bg_color = (50, 70, 110) if unlocked else (38, 42, 58)
        border = (255, 220, 120) if unlocked else (70, 78, 98)
        pygame.draw.rect(surface, bg_color, rect, border_radius=12)
        pygame.draw.rect(surface, border, rect, width=2, border_radius=12)

        icon_rect = pygame.Rect(rect.x + 14, rect.y + 12, 32, 32)
        icon_color = (255, 220, 120) if unlocked else (90, 98, 118)
        pygame.draw.rect(surface, icon_color, icon_rect, border_radius=8)
        if not unlocked:
            pygame.draw.rect(surface, (40, 44, 58), icon_rect.inflate(-14, -10), border_radius=4)

        name_color = (255, 240, 180) if unlocked else (150, 158, 178)
        desc_color = (220, 228, 245) if unlocked else (120, 128, 148)
        name = self.item_font.render(ach["name"], True, name_color)
        surface.blit(name, (rect.x + 60, rect.y + 8))
        desc = self.desc_font.render(ach["desc"], True, desc_color)
        surface.blit(desc, (rect.x + 60, rect.y + 32))

        status = "已解锁" if unlocked else "未解锁"
        st = self.desc_font.render(status, True, name_color)
        surface.blit(st, st.get_rect(midright=(rect.right - 14, rect.centery)))