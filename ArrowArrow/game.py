import pygame
import sys
import os
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

BG_TOP = (28, 32, 48)
BG_BOTTOM = (18, 20, 32)
TITLE_COLOR = (255, 220, 120)
TITLE_SHADOW = (0, 0, 0)
BTN_NORMAL = (70, 130, 200)
BTN_HOVER = (100, 170, 240)
BTN_TEXT = (255, 255, 255)

# ---------- 更可靠的中文字体加载 ----------
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
    "/System/Library/Fonts/PingFang.ttc",          # macOS
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux 文泉驿
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def get_font(size, bold=False):
    # 1) 尝试直接加载字体文件
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except Exception:
                continue
    # 2) 尝试 SysFont
    for name in ["Microsoft YaHei", "SimHei", "PingFang SC", "Arial Unicode MS", "Noto Sans CJK SC"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            # 简单验证能否渲染中文
            test = f.render("测试", True, (255, 255, 255))
            if test.get_width() > 0:
                return f
        except Exception:
            continue
    # 3) 最后兜底
    print("警告：未找到中文字体，中文可能无法显示")
    return pygame.font.Font(None, size)

title_font = get_font(72, bold=True)
btn_font = get_font(30, bold=True)
sub_font = get_font(22)

# ---------- 背景音乐 ----------
def load_bgm(path="bgm.mp3"):
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"背景音乐加载失败: {e}")
    else:
        print(f"未找到背景音乐文件: {path}，跳过播放")

# ---------- 箭头装饰 ----------
ARROW_COLOR = (110, 150, 210)
ARROW_SIZE = 26

def create_arrow_surface(direction, size=ARROW_SIZE, color=ARROW_COLOR):
    surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
    cx, cy = size, size
    half = size // 2
    shaft = pygame.Rect(cx - half, cy - 4, size, 8)
    head = [(cx + half, cy - 12), (cx + half + 14, cy), (cx + half, cy + 12)]
    pygame.draw.rect(surf, color, shaft, border_radius=3)
    pygame.draw.polygon(surf, color, head)
    angle_map = {"right": 0, "down": -90, "left": 180, "up": 90}
    return pygame.transform.rotate(surf, angle_map[direction])

ARROW_SURFACES = {d: create_arrow_surface(d) for d in ["up", "down", "left", "right"]}

class FloatingArrow:
    def __init__(self):
        self.reset(random_edge=True)

    def reset(self, random_edge=False):
        self.direction = random.choice(["up", "down", "left", "right"])
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
        if self.direction == "right":
            self.x += self.speed
        elif self.direction == "left":
            self.x -= self.speed
        elif self.direction == "down":
            self.y += self.speed
        else:
            self.y -= self.speed
        self.angle += self.rot_speed
        margin = 60
        if (self.x < -margin or self.x > WIDTH + margin or
                self.y < -margin or self.y > HEIGHT + margin):
            self.reset(random_edge=False)

    def draw(self, surface):
        base = ARROW_SURFACES[self.direction]
        w = int(base.get_width() * self.scale)
        h = int(base.get_height() * self.scale)
        img = pygame.transform.smoothscale(base, (w, h))
        img = pygame.transform.rotate(img, self.angle)
        img = img.copy()
        img.set_alpha(self.alpha)
        rect = img.get_rect(center=(self.x, self.y))
        surface.blit(img, rect)

# ---------- 按钮类 ----------
class Button:
    def __init__(self, text, center, size, callback):
        self.text = text
        self.base_rect = pygame.Rect(0, 0, *size)
        self.base_rect.center = center
        self.callback = callback
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
        text_surf = btn_font.render(self.text, True, BTN_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.base_rect.collidepoint(event.pos):
                self.callback()

# ---------- 渐变背景 ----------
def draw_gradient_bg(surface):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
        g = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
        b = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# ---------- 回调 ----------
def start_game():
    print("点击了：开始游戏")

def select_level():
    print("点击了：选择关卡")

def show_achievements():
    print("点击了：成就")

def show_settings():
    print("点击了：设置")

# ---------- 创建按钮（新布局） ----------
# 前两个按钮：同一列，水平居中
btn_w, btn_h = 220, 60
col_x = WIDTH // 2
row1_y = HEIGHT - 260
row2_y = HEIGHT - 180

start_btn = Button("开始游戏", (col_x, row1_y), (btn_w, btn_h), start_game)
level_btn = Button("选择关卡", (col_x, row2_y), (btn_w, btn_h), select_level)

# 第三行：成就 + 设置，同一行，中间有间隔
small_w, small_h = 150, 52
small_gap = 40
total_small_w = small_w * 2 + small_gap
left_x = WIDTH // 2 - total_small_w // 2 + small_w // 2
right_x = WIDTH // 2 + total_small_w // 2 - small_w // 2
row3_y = HEIGHT - 100

ach_btn = Button("成就", (left_x, row3_y), (small_w, small_h), show_achievements)
set_btn = Button("设置", (right_x, row3_y), (small_w, small_h), show_settings)

buttons = [start_btn, level_btn, ach_btn, set_btn]

# ---------- 主循环 ----------
def main():
    clock = pygame.time.Clock()
    load_bgm("bgm.mp3")

    arrows = [FloatingArrow() for _ in range(18)]

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for btn in buttons:
                btn.handle_event(event)

        for btn in buttons:
            btn.update(mouse_pos)

        for a in arrows:
            a.update()

        draw_gradient_bg(screen)

        for a in arrows:
            a.draw(screen)

        # 标题
        title_text = "一箭又一箭"
        shadow = title_font.render(title_text, True, TITLE_SHADOW)
        title = title_font.render(title_text, True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        screen.blit(shadow, title_rect.move(4, 4))
        screen.blit(title, title_rect)

        sub = sub_font.render("点击箭头，让它飞出棋盘", True, (180, 190, 210))
        sub_rect = sub.get_rect(center=(WIDTH // 2, 230))
        screen.blit(sub, sub_rect)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()