# settings.py
import json
import os
import pygame
from config import WIDTH, HEIGHT, BTN_NORMAL, BTN_HOVER, BTN_TEXT
from ui import Button, get_font

SAVE_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "sfx_volume": 80,
    "music_volume": 60,
    "sfx_enabled": True,
    "music_enabled": True,
}


class SettingsManager:
    def __init__(self, path=SAVE_FILE):
        self.path = path
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                for k in DEFAULT_SETTINGS:
                    if k in d:
                        self.data[k] = d[k]
            except Exception as e:
                print(f"设置读取失败: {e}")

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"设置写入失败: {e}")

    def apply_to_audio(self):
        """把设置应用到 pygame.mixer"""
        try:
            if self.data["music_enabled"]:
                pygame.mixer.music.set_volume(self.data["music_volume"] / 100.0)
                if not pygame.mixer.music.get_busy():
                    # 如果当前没在放，不强行播放；由 main 决定
                    pass
            else:
                pygame.mixer.music.set_volume(0.0)
        except Exception as e:
            print(f"音乐音量应用失败: {e}")
        # 音效音量：如果你以后用 Sound 对象，可以在这里统一设置


# ---------------- 滑块 ----------------
class Slider:
    def __init__(self, x, y, w, h, value, label, on_change=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.value = value          # 0~100
        self.label = label
        self.dragging = False
        self.on_change = on_change

    def _knob_x(self):
        return self.rect.x + int(self.rect.width * self.value / 100)

    def handle_event(self, event, offset=(0, 0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos[0] - offset[0], event.pos[1] - offset[1]
            knob = pygame.Rect(self._knob_x() - 8, self.rect.centery - 12, 16, 24)
            if knob.collidepoint(mx, my) or self.rect.collidepoint(mx, my):
                self.dragging = True
                self._update_value(mx)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                if self.on_change:
                    self.on_change(self.value)
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx = event.pos[0] - offset[0]
            self._update_value(mx)

    def _update_value(self, mx):
        t = (mx - self.rect.x) / self.rect.width
        t = max(0.0, min(1.0, t))
        self.value = int(t * 100)
        if self.on_change:
            self.on_change(self.value)

    def draw(self, surface, font):
        # 轨道
        track = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(surface, (60, 70, 95), track, border_radius=3)
        # 已填充
        filled = pygame.Rect(self.rect.x, self.rect.centery - 3,
                             int(self.rect.width * self.value / 100), 6)
        pygame.draw.rect(surface, BTN_HOVER, filled, border_radius=3)
        # 滑块
        knob_x = self._knob_x()
        pygame.draw.circle(surface, (255, 255, 255), (knob_x, self.rect.centery), 9)
        pygame.draw.circle(surface, BTN_NORMAL, (knob_x, self.rect.centery), 9, 2)
        # 标签和数值
        label = font.render(f"{self.label}", True, (230, 235, 245))
        surface.blit(label, (self.rect.x, self.rect.y - 26))
        val = font.render(f"{self.value}", True, (255, 220, 120))
        surface.blit(val, val.get_rect(midright=(self.rect.right, self.rect.y - 26)))


# ---------------- 复选框 ----------------
class Checkbox:
    def __init__(self, x, y, size, checked, label, on_toggle=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.checked = checked
        self.label = label
        self.on_toggle = on_toggle

    def handle_event(self, event, offset=(0, 0)):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos[0] - offset[0], event.pos[1] - offset[1]
            # 扩大点击区域到标签
            hit = self.rect.inflate(160, 0)
            if hit.collidepoint(mx, my):
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)

    def draw(self, surface, font):
        pygame.draw.rect(surface, (30, 34, 48), self.rect, border_radius=4)
        pygame.draw.rect(surface, (120, 140, 180), self.rect, width=2, border_radius=4)
        if self.checked:
            # 画对勾
            x, y, s = self.rect.x, self.rect.y, self.rect.width
            pygame.draw.lines(surface, (120, 255, 160), False, [
                (x + s * 0.2, y + s * 0.55),
                (x + s * 0.45, y + s * 0.78),
                (x + s * 0.8, y + s * 0.25),
            ], 3)
        label = font.render(self.label, True, (230, 235, 245))
        surface.blit(label, (self.rect.right + 10, self.rect.centery - label.get_height() // 2))


# ---------------- 弹窗 ----------------
class SettingsPopup:
    def __init__(self, manager: SettingsManager):
        self.manager = manager
        self.visible = False
        self.rect = pygame.Rect(0, 0, 420, 320)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

        f = get_font(26, bold=True)
        self.title_font = f
        self.item_font = get_font(20)
        self.small_font = get_font(18)

        # 两个滑块
        sx = self.rect.x + 40
        sw = self.rect.width - 80
        self.slider_sfx = Slider(sx, self.rect.y + 100, sw, 20,
                                 manager.data["sfx_volume"], "音效大小",
                                 on_change=self._on_sfx)
        self.slider_music = Slider(sx, self.rect.y + 170, sw, 20,
                                   manager.data["music_volume"], "音乐大小",
                                   on_change=self._on_music)

        # 两个复选框
        cb_y = self.rect.y + 240
        self.cb_sfx = Checkbox(self.rect.x + 50, cb_y, 26,
                               manager.data["sfx_enabled"], "开启音效",
                               on_toggle=self._on_sfx_toggle)
        self.cb_music = Checkbox(self.rect.x + 230, cb_y, 26,
                                 manager.data["music_enabled"], "开启音乐",
                                 on_toggle=self._on_music_toggle)

        # 关闭按钮
        self.close_btn = Button(
            "×",
            (self.rect.right - 26, self.rect.y + 22),
            (40, 40),
            self.close,
            font=get_font(28, bold=True)
        )

    # ---- 回调 ----
    def _on_sfx(self, v):
        self.manager.data["sfx_volume"] = v
        self.manager.save()

    def _on_music(self, v):
        self.manager.data["music_volume"] = v
        self.manager.save()
        self.manager.apply_to_audio()

    def _on_sfx_toggle(self, checked):
        self.manager.data["sfx_enabled"] = checked
        self.manager.save()

    def _on_music_toggle(self, checked):
        self.manager.data["music_enabled"] = checked
        self.manager.save()
        if checked:
            # 重新播放音乐
            try:
                if os.path.exists("music/duosuoleisi.mp3"):
                    pygame.mixer.music.load("music/duosuoleisi.mp3")
                    pygame.mixer.music.set_volume(self.manager.data["music_volume"] / 100.0)
                    pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"音乐恢复失败: {e}")
        else:
            pygame.mixer.music.stop()

    def open(self):
        self.visible = True
        # 同步最新值
        self.slider_sfx.value = self.manager.data["sfx_volume"]
        self.slider_music.value = self.manager.data["music_volume"]
        self.cb_sfx.checked = self.manager.data["sfx_enabled"]
        self.cb_music.checked = self.manager.data["music_enabled"]

    def close(self):
        self.visible = False

    # ---- 事件 ----
    def handle_event(self, event):
        if not self.visible:
            return False
        # 点击弹窗外关闭
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                self.close()
                return True
        self.close_btn.handle_event(event)
        self.slider_sfx.handle_event(event)
        self.slider_music.handle_event(event)
        self.cb_sfx.handle_event(event)
        self.cb_music.handle_event(event)
        return True

    def update(self, dt):
        if not self.visible:
            return
        self.close_btn.update(pygame.mouse.get_pos())

    # ---- 绘制 ----
    def draw(self, surface):
        if not self.visible:
            return
        # 半透明遮罩
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # 弹窗背景
        pygame.draw.rect(surface, (40, 46, 66), self.rect, border_radius=16)
        pygame.draw.rect(surface, (120, 160, 220), self.rect, width=2, border_radius=16)

        # 标题
        title = self.title_font.render("设置", True, (255, 220, 120))
        surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.y + 30)))

        # 滑块
        self.slider_sfx.draw(surface, self.item_font)
        self.slider_music.draw(surface, self.item_font)

        # 复选框
        self.cb_sfx.draw(surface, self.small_font)
        self.cb_music.draw(surface, self.small_font)

        # 关闭按钮外框（固定）
        cx, cy = self.rect.right - 26, self.rect.y + 26
        pygame.draw.circle(surface, (60, 70, 95), (cx, cy), 20)
        pygame.draw.circle(surface, (200, 210, 230), (cx, cy), 20, 2)
        self.close_btn.draw(surface)