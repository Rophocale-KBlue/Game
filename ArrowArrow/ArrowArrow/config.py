# config.py
WIDTH, HEIGHT = 800, 600

BG_TOP = (28, 32, 48)
BG_BOTTOM = (18, 20, 32)
TITLE_COLOR = (255, 220, 120)
TITLE_SHADOW = (0, 0, 0)
BTN_NORMAL = (70, 130, 200)
BTN_HOVER = (100, 170, 240)
BTN_TEXT = (255, 255, 255)

GRID_LINE = (60, 70, 95)
CELL_BG = (35, 40, 58)
ARROW_COLOR = (120, 200, 255)
ARROW_BLOCKED = (255, 90, 90)
ARROW_FLYING = (120, 255, 160)

DIRS = {
    "up":    (0, -1),
    "down":  (0, 1),
    "left":  (-1, 0),
    "right": (1, 0),
}

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

LEVELS = [
    {
        "name": "第一关",
        "grid_size": 3,
        "mistakes": 3,
        "arrows": [
            (0, 0, "right"),
            (1, 1, "up"),
            (2, 2, "left"),
        ],
    },
    {
        "name": "第二关",
        "grid_size": 4,
        "mistakes": 4,
        "arrows": [
            (0, 0, "right"), (0, 3, "down"),
            (1, 1, "up"),   (1, 2, "left"),
            (2, 0, "right"), (2, 3, "up"),
            (3, 1, "left"),  (3, 2, "down"),
            (0, 2, "down"),  (2, 1, "right"),
        ],
    },
    {
        "name": "第三关",
        "grid_size": 5,
        "mistakes": 5,
        "arrows": [
            (0, 0, "right"), (0, 2, "down"), (0, 4, "left"),
            (1, 1, "up"),    (1, 3, "down"),
            (2, 0, "right"), (2, 2, "up"),   (2, 4, "left"),
            (3, 1, "down"),  (3, 3, "up"),
            (4, 0, "right"), (4, 2, "down"), (4, 4, "left"),
            (0, 1, "down"),  (1, 4, "left"),
            (2, 3, "up"),    (3, 0, "right"),
            (4, 1, "up"),    (1, 0, "right"), (3, 4, "left"),
        ],
    },
]

# ---------- 成就定义 ----------
# check 函数接收 progress 字典，返回 bool
ACHIEVEMENTS = [
    {
        "id": "clear_level_1",
        "name": "初出茅庐",
        "desc": "完成第一关",
        "check": lambda p: 0 in p["cleared_levels"],
    },
    {
        "id": "clear_level_2",
        "name": "小试牛刀",
        "desc": "完成第二关",
        "check": lambda p: 1 in p["cleared_levels"],
    },
    {
        "id": "clear_level_3",
        "name": "箭无虚发",
        "desc": "完成第三关",
        "check": lambda p: 2 in p["cleared_levels"],
    },
    {
        "id": "fly_50",
        "name": "百步穿杨",
        "desc": "累计飞出 50 个箭头",
        "check": lambda p: p["total_arrows_flew"] >= 50,
    },
    {
        "id": "all_achievements",
        "name": "全成就",
        "desc": "解锁前四个成就",
        "check": lambda p: all(
            aid in p["unlocked"]
            for aid in ["clear_level_1", "clear_level_2", "clear_level_3", "fly_50"]
        ),
    },
]

ACHIEVEMENT_BY_ID = {a["id"]: a for a in ACHIEVEMENTS}