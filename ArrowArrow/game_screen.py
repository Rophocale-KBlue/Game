# game_screen.py
import math
import pygame
import random
from config import (
    WIDTH, HEIGHT, LEVELS, DIRS, CELL_BG, GRID_LINE,
    ARROW_COLOR, ARROW_BLOCKED, ARROW_FLYING
)
from ui import Button, get_font, draw_gradient_bg
from achievements import AchievementManager

CELL_LIGHT = (245, 235, 215)   # 米白色
CELL_DARK = (190, 170, 145)    # 灰褐色
BOARD_BORDER = (170, 140, 90)  # 卡其色边框

def generate_random_level(grid_size, arrow_count):
    """
    生成保证可解的关卡
    方法：
    1. 随机生成箭头位置
    2. 随机生成方向
    3. 检查是否存在解
    4. 不可解则重新生成
    """
    directions = list(DIRS.keys())
    def create_once():
        arrows = []
        # 随机选择位置
        cells = [
            (r, c)
            for r in range(grid_size)
            for c in range(grid_size)
        ]
        random.shuffle(cells)
        for i in range(min(arrow_count, len(cells))):
            r, c = cells[i]
            d = random.choice(directions)
            arrows.append(
                (r, c, d)
            )
        return arrows
    def path_clear(target, current):
        r, c, d = target
        dr, dc = DIRS[d]
        r += dr
        c += dc
        while (
            0 <= r < grid_size
            and
            0 <= c < grid_size
        ):
            for ar, ac, ad in current:
                if ar == r and ac == c:
                    return False
            r += dr
            c += dc
        return True
    def can_finish(test_arrows):
        remaining = test_arrows.copy()
        while remaining:
            found = False
            for arrow in remaining:
                if path_clear(
                    arrow,
                    remaining
                ):
                    remaining.remove(arrow)
                    found = True
                    break
            # 没有任何箭头可以出去
            if not found:
                return False
        return True
    # 不断尝试直到生成可解地图
    while True:
        result = create_once()
        if can_finish(result):
            return result

class _GameArrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.state = "idle"
        self.anim_t = 0.0
        self.offset = [0.0, 0.0]
        self.blocked_timer = 0.0

    def start_flying(self):
        self.state = "flying"
        self.anim_t = 0.0

    def start_blocked(self):
        self.state = "blocked"
        self.blocked_timer = 0.0

    def update(self, dt):
        if self.state == "flying":
            self.anim_t += dt * 6
            dr, dc = DIRS[self.direction]
            self.offset[0] += dc * 14
            self.offset[1] += dr * 14
            if self.anim_t > 1.0:
                self.state = "gone"
        elif self.state == "blocked":
            self.blocked_timer += dt
            shake = math.sin(self.blocked_timer * 30) * 6
            dr, dc = DIRS[self.direction]
            self.offset[0] = -dc * shake
            self.offset[1] = dr * shake
            if self.blocked_timer > 0.4:
                self.state = "idle"
                self.offset = [0.0, 0.0]

class GameScreen:
    def __init__(self, level_index, on_back, achievement_manager=None, settings_manager=None):
        self.background = pygame.image.load("image/game_background.png").convert()
        self.level_index = level_index
        self.fail_sound = pygame.mixer.Sound("music/ngm.mp3")
        self.fail_sound.set_volume(0.8)
        self.fail_sound_played = False
        self.time_limit = LEVELS[level_index].get("time_limit",None)
        self.remaining_time = self.time_limit
        self.on_back = on_back
        self.ach = achievement_manager or AchievementManager()
        self.settings_manager = settings_manager
        self.load_level(level_index)
        self.restart_btn = Button("重新开始", (WIDTH - 110, 60), (160, 46), self.restart)
        self.back_btn = Button("返回主菜单", (WIDTH - 100, 120), (160, 100), self.on_back,image="image/back_menu.png")
        self.hud_font = get_font(22)
        self.sub_font = get_font(22)
        self.unlock_toast_timer = 0.0   # 剩余总时间
        self.unlock_toast_text = ""
        self.unlock_toast_duration = 2.5  # 总时长
        self.unlock_toast_slide = 0.0   #滑入进度，范围在0-1

    def load_level(self, index):
        self.level_index = index
        data = LEVELS[index]
        self.grid_size = data["grid_size"]
        self.mistakes_left = data["mistakes"]
        self.max_mistakes = data["mistakes"]
        self.arrows = [
            _GameArrow(r, c, d)
            for (r, c, d) in generate_random_level(data["grid_size"], data["arrow_count"])
        ]
        self.status = "playing"
        self.time_limit = LEVELS[index].get("time_limit", None)
        self.remaining_time = self.time_limit
        self.result_timer = 0.0
        max_board = 460
        self.cell_size = max_board // self.grid_size
        board_px = self.cell_size * self.grid_size
        self.board_x = (WIDTH - board_px) // 2
        self.board_y = 140
        self.level_cleared_reported = False
        self.unlock_toast_timer = 0.0
        self.unlock_toast_text = ""
        self.unlock_toast_slide = 0.0

    def cell_center(self, row, col):
        cx = self.board_x + col * self.cell_size + self.cell_size // 2
        cy = self.board_y + row * self.cell_size + self.cell_size // 2
        return cx, cy

    def arrow_at(self, row, col, only_idle=False):
        for a in self.arrows:
            if a.row == row and a.col == col:
                if a.state == "gone":
                    continue
                if only_idle and a.state != "idle":
                    continue
                return a
        return None

    def is_path_clear(self, arrow):
        dr, dc = DIRS[arrow.direction]
        r, c = arrow.row + dr, arrow.col + dc

        while 0 <= r < self.grid_size and 0 <= c < self.grid_size:
            target = self.arrow_at(r, c)
            if target is not None:
                return False
            r += dr
            c += dc
        return True

    def click_cell(self, row, col):
        if self.status != "playing":
            return
        arrow = self.arrow_at(row, col)
        if arrow is None or arrow.state != "idle":
            return
        if self.is_path_clear(arrow):
            arrow.start_flying()
            self.ach.on_arrow_flew(1)
        else:
            arrow.start_blocked()
            self.mistakes_left -= 1
            if self.mistakes_left <= 0:
                self.status = "lose"
                if not self.fail_sound_played:
                    if self.settings_manager:
                        if self.settings_manager.data["sfx_enabled"]:
                            self.fail_sound.set_volume(self.settings_manager.data["sfx_volume"] / 100)
                            self.fail_sound.play()
                    else:
                        self.fail_sound.play()
                    self.fail_sound_played = True
                self.result_timer = 0.0


    def restart(self):
        self.load_level(self.level_index)
        self.time_limit = LEVELS[self.level_index].get("time_limit", None)
        self.remaining_time = self.time_limit
        self.fail_sound_played = False

    def next_level(self):
        if self.level_index + 1 < len(LEVELS):
            self.load_level(
                self.level_index + 1
            )
        else:
            # 关卡全部完成
            self.status = "finished"
            self.result_timer = 0.0

    def handle_event(self, event):
        self.restart_btn.handle_event(event)
        self.back_btn.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.status == "playing":
                mx, my = event.pos
                board_px = self.cell_size * self.grid_size
                if (self.board_x <= mx < self.board_x + board_px and
                        self.board_y <= my < self.board_y + board_px):
                    col = (mx - self.board_x) // self.cell_size
                    row = (my - self.board_y) // self.cell_size
                    self.click_cell(row, col)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart()
            elif event.key == pygame.K_n and self.status == "win":
                self.next_level()

    def update(self, dt):
        # 倒计时
        if self.time_limit is not None and self.status == "playing":
            self.remaining_time -= dt
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.status = "lose"
                if not self.fail_sound_played:
                    self.fail_sound.play()
                    self.fail_sound_played = True
        #鼠标控制
        mp = pygame.mouse.get_pos()
        self.restart_btn.update(mp)
        self.back_btn.update(mp)
        #箭头
        for a in self.arrows:
            a.update(dt)
        if self.status == "playing":
            if all(a.state == "gone" for a in self.arrows):
                if self.level_index + 1 >= len(LEVELS):
                    # 最后一关完成
                    self.status = "finished"
                    self.result_timer = 0.0
                else:
                    self.status = "win"
                    self.result_timer = 0.0
                if not self.level_cleared_reported:
                    self.level_cleared_reported = True
                    self.ach.on_level_cleared(self.level_index)
        if self.status in ("win", "lose"):
            self.result_timer += dt
        elif self.status == "finished":
            self.result_timer += dt
            if self.result_timer >= 2.0:
                self.on_back()

        # 解锁成就提示
        new_ones = self.ach.consume_newly_unlocked()
        if new_ones:
            names = "、".join(a["name"] for a in new_ones)
            # 如果已有提示，追加而不是覆盖
            if self.unlock_toast_timer > 0:
                self.unlock_toast_text += "、" + names
            else:
                self.unlock_toast_text = names
            self.unlock_toast_timer = self.unlock_toast_duration
            self.unlock_toast_slide = 0.0

        if self.unlock_toast_timer > 0:
            self.unlock_toast_timer -= dt
            # 滑入进度：前 0.25 秒从 0 → 1
            self.unlock_toast_slide = min(1.0, self.unlock_toast_slide + dt / 0.25)
            if self.unlock_toast_timer <= 0:
                self.unlock_toast_text = ""
                self.unlock_toast_slide = 0.0

    def draw_arrow(self, surface, cx, cy, direction, color):
        size = self.cell_size * 0.55
        half = size // 2
        surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
        scx, scy = size, size
        shaft = pygame.Rect(scx - half, scy - size * 0.12, size, size * 0.24)
        head_len = size * 0.5
        head = [
            (scx + half, scy - size * 0.35),
            (scx + half + head_len, scy),
            (scx + half, scy + size * 0.35),
        ]
        pygame.draw.rect(surf, color, shaft, border_radius=int(size * 0.1))
        pygame.draw.polygon(surf, color, head)
        angle_map = {"right": 0, "up": 90, "down": -90, "left": 180}
        rotated = pygame.transform.rotate(surf, angle_map[direction])
        surface.blit(rotated, rotated.get_rect(center=(cx, cy)))

    def draw(self, surface):
        bg = pygame.transform.smoothscale(self.background,surface.get_size())
        surface.blit(bg, (0, 0))
        level_name = LEVELS[self.level_index]["name"]
        remaining = sum(1 for a in self.arrows if a.state != "gone")
        hud = self.hud_font.render(f"{level_name}   剩余箭头: {remaining}", True, (230, 235, 245))
        if self.time_limit is not None:
            minutes = int(self.remaining_time) // 60
            seconds = int(self.remaining_time) % 60
            timer = self.hud_font.render(f"时间:{minutes:02d}:{seconds:02d}", True, (255, 220, 100))
            surface.blit(timer, (30, 90))
        surface.blit(hud, (30, 24))
        mistakes = self.hud_font.render(f"失误剩余: {self.mistakes_left} / {self.max_mistakes}", True, (255, 180, 120))
        surface.blit(mistakes, (30, 56))

        board_px = self.cell_size * self.grid_size
        board_rect = pygame.Rect(self.board_x, self.board_y, board_px, board_px)
        pygame.draw.rect(surface, CELL_BG, board_rect, border_radius=10)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = self.board_x + col * self.cell_size
                y = self.board_y + row * self.cell_size
                rect = pygame.Rect(
                    x,
                    y,
                    self.cell_size,
                    self.cell_size
                )
                if (row + col) % 2 == 0:
                    color = CELL_LIGHT
                else:
                    color = CELL_DARK
                pygame.draw.rect(
                    surface,
                    color,
                    rect
                )
        # 绘制棋盘网格线
        for i in range(self.grid_size + 1):
            x = self.board_x + i * self.cell_size
            y = self.board_y + i * self.cell_size
            pygame.draw.line(
                surface,
                GRID_LINE,
                (x, self.board_y),
                (x, self.board_y + board_px),
                2
            )
            pygame.draw.line(
                surface,
                GRID_LINE,
                (self.board_x, y),
                (self.board_x + board_px, y),
                2
            )
        #绘制边框
        pygame.draw.rect(
            surface,
            BOARD_BORDER,
            board_rect,
            width=12,
            border_radius=12
        )

        for a in self.arrows:
            if a.state == "gone":
                continue
            cx, cy = self.cell_center(a.row, a.col)
            cx += a.offset[0]
            cy += a.offset[1]
            color = ARROW_COLOR
            if a.state == "blocked":
                color = ARROW_BLOCKED
            elif a.state == "flying":
                color = ARROW_FLYING
            self.draw_arrow(surface, cx, cy, a.direction, color)

        self.restart_btn.draw(surface)
        self.back_btn.draw(surface)

        if self.status == "win":
            self._draw_result(surface, "通关！", (120, 255, 160))
        elif self.status == "lose":
            self._draw_result(surface, "失败", (255, 110, 110))
        elif self.status == "finished":
            self._draw_result(surface,"全部通关！",(255, 220, 100))
        if self.unlock_toast_timer > 0:
            self._draw_unlock_toast(surface)

    def _draw_result(self, surface, text, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))
        big = get_font(60, bold=True)
        t = big.render(text, True, color)
        surface.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        if self.status == "win":
            if self.level_index + 1 < len(LEVELS):
                tip = self.sub_font.render("按 N 进入下一关，或按 R 重新开始", True, (230, 235, 245))
        elif self.status == "finished":
            tip = self.sub_font.render("即将返回主菜单", True, (230, 235, 245))
        else:
            tip = self.sub_font.render("按 R 重新开始", True, (230, 235, 245))
        surface.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

    def _draw_unlock_toast(self, surface):
        if not self.unlock_toast_text:
            return

        font_title = get_font(16, bold=True)
        font_name = get_font(20, bold=True)

        title_surf = font_title.render("成就解锁", True, (255, 220, 120))
        name_surf = font_name.render(self.unlock_toast_text, True, (255, 245, 210))

        pad_x, pad_y = 16, 12
        icon_size = 28
        gap = 12
        text_w = max(title_surf.get_width(), name_surf.get_width())
        w = pad_x * 2 + icon_size + gap + text_w
        h = pad_y * 2 + title_surf.get_height() + name_surf.get_height() + 4

        # 目标位置：右上角
        target_x = WIDTH - w - 20
        target_y = 20

        # 滑入：从右侧屏幕外滑到目标位置
        slide_offset = int((1.0 - self.unlock_toast_slide) * (w + 40))
        x = target_x + slide_offset
        y = target_y
        rect = pygame.Rect(x, y, w, h)

        # 透明度
        if self.unlock_toast_timer < 0.5:
            alpha = int(255 * (self.unlock_toast_timer / 0.5))
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        # 背景
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(bg, (45, 38, 20, int(alpha * 0.92)), bg.get_rect(), border_radius=14)
        pygame.draw.rect(bg, (255, 220, 120, alpha), bg.get_rect(), width=2, border_radius=14)
        surface.blit(bg, rect.topleft)

        # 图标（金色圆角方块 + 箭头）
        icon_rect = pygame.Rect(rect.x + pad_x, rect.y + (h - icon_size) // 2, icon_size, icon_size)
        icon_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        pygame.draw.rect(icon_surf, (255, 220, 120, alpha), icon_surf.get_rect(), border_radius=8)
        # 简单画个向右的箭头
        ac = (60, 45, 10, alpha)
        pygame.draw.polygon(icon_surf, ac, [
            (7, 14), (16, 14), (16, 9), (23, 16),
            (16, 23), (16, 18), (7, 18)
        ])
        surface.blit(icon_surf, icon_rect.topleft)

        # 文字
        tx = icon_rect.right + gap
        title_surf = title_surf.copy()
        title_surf.set_alpha(alpha)
        name_surf = name_surf.copy()
        name_surf.set_alpha(alpha)
        surface.blit(title_surf, (tx, rect.y + pad_y))
        surface.blit(name_surf, (tx, rect.y + pad_y + title_surf.get_height() + 4))