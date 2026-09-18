# main.py
import sys
import os
import pygame

from config import WIDTH, HEIGHT
from start_screen import StartScreen
from level_select import LevelSelectScreen
from game_screen import GameScreen
from achievements import AchievementManager, AchievementScreen

STATE_START = "start"
STATE_LEVEL_SELECT = "level_select"
STATE_GAME = "game"
STATE_ACHIEVEMENT = "achievement"

def load_bgm(path="bgm.mp3"):
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error as e:
            print(f"背景音乐加载失败: {e}")

class App:
    def __init__(self):
        self.state = STATE_START

        # 唯一的成就管理器，所有界面共享
        self.ach_manager = AchievementManager()

        self.start_screen = StartScreen(
            on_start=self.go_game_first,
            on_level_select=self.go_level_select,
            on_achievement=self.go_achievement,
            on_settings=lambda: print("设置暂未实现"),
        )
        self.level_select_screen = LevelSelectScreen(
            on_select_level=self.start_level,
            on_back=self.go_start,
        )
        self.achievement_screen = AchievementScreen(
            on_back=self.go_start,
            achievement_manager=self.ach_manager,
        )
        self.game_screen = None

    def go_start(self):
        self.state = STATE_START

    def go_level_select(self):
        self.state = STATE_LEVEL_SELECT

    def go_achievement(self):
        self.state = STATE_ACHIEVEMENT

    def go_game_first(self):
        self.start_level(0)

    def start_level(self, index):
        self.game_screen = GameScreen(
            index,
            on_back=self.go_start,
            achievement_manager=self.ach_manager,
        )
        self.state = STATE_GAME

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
        if self.state == STATE_START:
            self.start_screen.handle_event(event)
        elif self.state == STATE_LEVEL_SELECT:
            self.level_select_screen.handle_event(event)
        elif self.state == STATE_GAME and self.game_screen:
            self.game_screen.handle_event(event)
        elif self.state == STATE_ACHIEVEMENT:
            self.achievement_screen.handle_event(event)
        return True

    def update(self, dt):
        if self.state == STATE_START:
            self.start_screen.update(dt)
        elif self.state == STATE_LEVEL_SELECT:
            self.level_select_screen.update(dt)
        elif self.state == STATE_GAME and self.game_screen:
            self.game_screen.update(dt)
        elif self.state == STATE_ACHIEVEMENT:
            self.achievement_screen.update(dt)

    def draw(self, surface):
        if self.state == STATE_START:
            self.start_screen.draw(surface)
        elif self.state == STATE_LEVEL_SELECT:
            self.level_select_screen.draw(surface)
        elif self.state == STATE_GAME and self.game_screen:
            self.game_screen.draw(surface)
        elif self.state == STATE_ACHIEVEMENT:
            self.achievement_screen.draw(surface)

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("一箭又一箭")
    load_bgm("bgm.mp3")

    clock = pygame.time.Clock()
    app = App()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if not app.handle_event(event):
                running = False
        app.update(dt)
        app.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()