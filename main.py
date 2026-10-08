import pygame
import sys
import json
import os
import math
import random

# ============================================================
#   CIGARETTE CLICKER v3 — с финалом
#   Игра НЕ пропагандирует курение!
# ============================================================

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 480, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cigarette Clicker — Курение убивает!")
clock = pygame.time.Clock()

# ---------- ЦВЕТА ----------
WHITE       = (255, 255, 255)
BLACK       = (0, 0, 0)
RED         = (200, 40, 40)
DARK_RED    = (120, 15, 15)
BRIGHT_RED  = (230, 60, 60)
GOLD        = (255, 200, 60)
GRAY        = (120, 120, 120)
LIGHT_GRAY  = (200, 200, 200)
DARK        = (25, 25, 30)
CREAM       = (240, 235, 220)

BG_TOP      = (30, 30, 40)
BG_BOTTOM   = (60, 40, 40)


# ---------- ШРИФТЫ ----------
def get_font(size, bold=False):
    for name in ["Arial", "DejaVu Sans", "Verdana", "Tahoma"]:
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_huge  = get_font(58, bold=True)
font_big   = get_font(40, bold=True)
font_med   = get_font(26, bold=True)
font_norm  = get_font(22)
font_small = get_font(18)
font_tiny  = get_font(14)
font_micro = get_font(11)


# ============================================================
#   ИКОНКА ОКНА
# ============================================================
def make_window_icon(size=64):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    r = size // 2 - 2
    pygame.draw.circle(surf, (200, 25, 25), (c, c), r)
    pygame.draw.circle(surf, (255, 255, 255), (c, c), r - 4)
    cw, ch = int(size * 0.68), int(size * 0.16)
    cg = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.rect(cg, (245, 245, 240), (0, 0, int(cw*0.7), ch))
    pygame.draw.rect(cg, (200, 200, 195), (0, 0, int(cw*0.7), ch), 1)
    pygame.draw.rect(cg, (220, 170, 90), (int(cw*0.7), 0, int(cw*0.3), ch))
    pygame.draw.rect(cg, (160, 110, 50), (int(cw*0.7), 0, int(cw*0.3), ch), 1)
    pygame.draw.circle(cg, (255, 80, 30), (int(cw*0.7) - 2, ch//2), ch//3)
    surf.blit(cg, (c - cw//2, c - ch//2))
    lw = max(4, size // 12)
    pygame.draw.line(surf, (200, 20, 20),
                     (c - r + 6, c - r + 6), (c + r - 6, c + r - 6), lw)
    pygame.draw.line(surf, (200, 20, 20),
                     (c - r + 6, c + r - 6), (c + r - 6, c - r + 6), lw)
    return surf

pygame.display.set_icon(make_window_icon(64))


# ============================================================
#   КОНФИГ ПАЧЕК
# ============================================================
PACK_TYPES = [
    {"id": 0, "name": "ПРИМА",         "body": (180, 180, 170), "lid": (220, 220, 210),
     "accent": (60, 60, 60),   "mult": 1,   "price": 0},
    {"id": 1, "name": "ЛМ",            "body": (200, 200, 200), "lid": (230, 230, 230),
     "accent": (30, 80, 160),  "mult": 2,   "price": 500},
    {"id": 2, "name": "BOND",          "body": (40, 40, 60),    "lid": (200, 180, 50),
     "accent": (230, 200, 60), "mult": 4,   "price": 2500},
    {"id": 3, "name": "Marlboro",      "body": (180, 30, 30),   "lid": (240, 240, 240),
     "accent": (40, 40, 40),   "mult": 8,   "price": 12000},
    {"id": 4, "name": "Parliament",    "body": (30, 60, 130),   "lid": (240, 240, 240),
     "accent": (200, 200, 200), "mult": 16, "price": 60000},
    {"id": 5, "name": "Dunhill",       "body": (60, 20, 20),    "lid": (220, 180, 120),
     "accent": (200, 160, 60), "mult": 30,  "price": 300000},
    {"id": 6, "name": "Davidoff",      "body": (20, 20, 20),    "lid": (200, 160, 60),
     "accent": (220, 180, 70), "mult": 60,  "price": 1500000},
    {"id": 7, "name": "PREMIUM BLACK", "body": (10, 10, 10),    "lid": (180, 140, 30),
     "accent": (255, 210, 80), "mult": 120, "price": 8000000},
]

# 🎯 ФИНАЛЬНАЯ ЦЕЛЬ
FINAL_TARGET = 10_000_000


def make_pack_surface(pack_cfg, w=240, h=340, open_lid=False):
    body_col = pack_cfg["body"]
    lid_col  = pack_cfg["lid"]
    accent   = pack_cfg["accent"]
    name     = pack_cfg["name"]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    lid_h = int(h * 0.22)
    if open_lid:
        lid_h = int(h * 0.14)

    # КОРПУС
    for x in range(w):
        t = x / w
        shade = 1.0 - 0.40 * (t ** 1.6)
        col = (int(body_col[0]*shade), int(body_col[1]*shade), int(body_col[2]*shade))
        pygame.draw.line(surf, col, (x, lid_h), (x, h))

    # КРЫШКА
    for x in range(w):
        t = x / w
        shade = 1.0 - 0.30 * (t ** 1.6)
        col = (int(lid_col[0]*shade), int(lid_col[1]*shade), int(lid_col[2]*shade))
        pygame.draw.line(surf, col, (x, 0), (x, lid_h))

    # Тень под крышкой
    for i in range(8):
        alpha = int(80 * (1 - i / 8))
        s = pygame.Surface((w, 1), pygame.SRCALPHA)
        s.fill((0, 0, 0, alpha))
        surf.blit(s, (0, lid_h + i))

    # НАЗВАНИЕ
    plate_w = int(w * 0.80)
    plate_h = max(26, int(lid_h * 0.55))
    plate_y = lid_h // 2 - plate_h // 2
    plate_x = (w - plate_w) // 2
    pygame.draw.rect(surf, (250, 250, 248),
                     (plate_x, plate_y, plate_w, plate_h), border_radius=6)
    pygame.draw.rect(surf, accent,
                     (plate_x, plate_y, plate_w, plate_h), 2, border_radius=6)
    f_size = max(12, min(22, int(plate_h * 0.7)))
    f = get_font(f_size, bold=True)
    txt = f.render(name, True, accent)
    while txt.get_width() > plate_w - 12 and f_size > 8:
        f_size -= 2
        f = get_font(f_size, bold=True)
        txt = f.render(name, True, accent)
    surf.blit(txt, (w // 2 - txt.get_width() // 2,
                    plate_y + plate_h // 2 - txt.get_height() // 2))

    # ДЕКОРАТИВНАЯ ПОЛОСА
    stripe_y = int(h * 0.46)
    stripe_h = 18
    pygame.draw.rect(surf, accent, (0, stripe_y, w, stripe_h))
    pygame.draw.rect(surf, (0, 0, 0), (0, stripe_y, w, stripe_h), 2)
    pygame.draw.line(surf, (255, 220, 100),
                     (0, stripe_y + stripe_h // 2),
                     (w, stripe_y + stripe_h // 2), 2)

    # ПРЕДУПРЕЖДАЮЩАЯ ПЛАШКА
    warn_y = int(h * 0.60)
    warn_h = int(h * 0.18)
    pygame.draw.rect(surf, (250, 250, 250),
                     (int(w * 0.06), warn_y, int(w * 0.88), warn_h),
                     border_radius=6)
    pygame.draw.rect(surf, (0, 0, 0),
                     (int(w * 0.06), warn_y, int(w * 0.88), warn_h),
                     2, border_radius=6)
    line1 = font_micro.render("КУРЕНИЕ", True, (0, 0, 0))
    line2 = font_micro.render("ВРЕДИТ", True, (0, 0, 0))
    line3 = font_micro.render("ЗДОРОВЬЮ", True, (0, 0, 0))
    cx = w // 2
    lh = line1.get_height() + 2
    surf.blit(line1, (cx - line1.get_width()//2, warn_y + 8))
    surf.blit(line2, (cx - line2.get_width()//2, warn_y + 8 + lh))
    surf.blit(line3, (cx - line3.get_width()//2, warn_y + 8 + lh*2))

    # ЗНАК ПЕРЕЧЁРКНУТОЙ СИГАРЕТЫ
    ic_y = int(h * 0.86)
    ic_r = 20
    pygame.draw.circle(surf, (255, 255, 255), (cx, ic_y), ic_r)
    pygame.draw.circle(surf, (200, 20, 20), (cx, ic_y), ic_r, 3)
    pygame.draw.line(surf, (200, 160, 100),
                     (cx - 12, ic_y + 5), (cx + 12, ic_y - 5), 4)
    pygame.draw.line(surf, (255, 140, 30),
                     (cx + 9, ic_y - 4), (cx + 12, ic_y - 5), 4)
    pygame.draw.line(surf, (200, 20, 20),
                     (cx - 14, ic_y - 14), (cx + 14, ic_y + 14), 3)
    pygame.draw.line(surf, (200, 20, 20),
                     (cx - 14, ic_y + 14), (cx + 14, ic_y - 14), 3)

    # КОНТУР
    pygame.draw.rect(surf, (30, 30, 30), (0, 0, w, h), 4, border_radius=10)
    pygame.draw.rect(surf, (100, 100, 100), (0, 0, w, h), 1, border_radius=10)

    # БЛИК
    gloss = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(25):
        alpha = int(45 * (1 - i / 25))
        pygame.draw.line(gloss, (255, 255, 255, alpha),
                         (int(w * 0.08) + i, int(h * 0.28)),
                         (int(w * 0.08) + i, int(h * 0.78)))
    surf.blit(gloss, (0, 0))
    return surf


print("Генерация текстур пачек...")
PACK_IMAGES = {cfg["id"]: make_pack_surface(cfg) for cfg in PACK_TYPES}
PACK_IMAGES_OPEN = {cfg["id"]: make_pack_surface(cfg, open_lid=True) for cfg in PACK_TYPES}


# ============================================================
#   ИКОНКИ
# ============================================================
def make_warning_icon(size=180):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    r = size // 2 - 6
    pygame.draw.circle(surf, (200, 20, 20), (c, c), r, 10)
    pygame.draw.circle(surf, (255, 255, 255), (c, c), r - 6)
    cw, ch = int(size * 0.62), int(size * 0.14)
    cg = pygame.Surface((cw, ch), pygame.SRCALPHA)
    pygame.draw.rect(cg, (245, 245, 240), (0, 0, int(cw*0.72), ch), border_radius=3)
    pygame.draw.rect(cg, (180, 180, 180), (0, 0, int(cw*0.72), ch), 2, border_radius=3)
    pygame.draw.rect(cg, (220, 170, 90), (int(cw*0.72), 0, int(cw*0.28), ch), border_radius=3)
    pygame.draw.rect(cg, (160, 110, 50), (int(cw*0.72), 0, int(cw*0.28), ch), 2, border_radius=3)
    pygame.draw.circle(cg, (255, 90, 30), (int(cw*0.72) - 2, ch // 2), ch // 3)
    cg = pygame.transform.rotate(cg, -25)
    surf.blit(cg, (c - cg.get_width() // 2, c - cg.get_height() // 2))
    pygame.draw.line(surf, (200, 20, 20),
                     (c - int(r*0.7), c - int(r*0.7)),
                     (c + int(r*0.7), c + int(r*0.7)), 14)
    pygame.draw.line(surf, (200, 20, 20),
                     (c - int(r*0.7), c + int(r*0.7)),
                     (c + int(r*0.7), c - int(r*0.7)), 14)
    return surf


def make_lungs_icon(size=110, healthy=False):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    left = pygame.Rect(int(size*0.10), int(size*0.25), int(size*0.36), int(size*0.60))
    right = pygame.Rect(int(size*0.54), int(size*0.25), int(size*0.36), int(size*0.60))
    base_col = (230, 130, 140) if healthy else (90, 45, 45)
    border_col = (170, 70, 80) if healthy else (45, 20, 20)
    spot_col = (255, 180, 190) if healthy else (30, 10, 10)
    for rect in (left, right):
        pygame.draw.ellipse(surf, base_col, rect)
        pygame.draw.ellipse(surf, border_col, rect, 4)
        for _ in range(6 if not healthy else 4):
            x = random.randint(rect.x + 6, rect.right - 6)
            y = random.randint(rect.y + 6, rect.bottom - 6)
            pygame.draw.circle(surf, spot_col, (x, y), random.randint(2, 5))
    trach_col = (180, 120, 130) if healthy else (120, 70, 70)
    line_col = (120, 60, 70) if healthy else (60, 30, 30)
    pygame.draw.rect(surf, trach_col,
                     (size//2 - 6, int(size*0.10), 12, int(size*0.30)),
                     border_radius=4)
    pygame.draw.line(surf, line_col,
                     (size//2, int(size*0.10)),
                     (size//2 - 20, int(size*0.35)), 4)
    pygame.draw.line(surf, line_col,
                     (size//2, int(size*0.10)),
                     (size//2 + 20, int(size*0.35)), 4)
    return surf


def make_skull_icon(size=80):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, int(size * 0.42)
    r = int(size * 0.28)
    pygame.draw.circle(surf, (240, 240, 235), (cx, cy), r)
    pygame.draw.circle(surf, (60, 60, 60), (cx, cy), r, 3)
    pygame.draw.rect(surf, (240, 240, 235),
                     (cx - r//2, cy + r//2 - 4, r, r//2 + 6), border_radius=6)
    pygame.draw.rect(surf, (60, 60, 60),
                     (cx - r//2, cy + r//2 - 4, r, r//2 + 6), 3, border_radius=6)
    pygame.draw.circle(surf, (30, 30, 30), (cx - r//2, cy - 4), r//5)
    pygame.draw.circle(surf, (30, 30, 30), (cx + r//2, cy - 4), r//5)
    pygame.draw.polygon(surf, (30, 30, 30),
                        [(cx, cy + 2), (cx - 5, cy + 12), (cx + 5, cy + 12)])
    for i in range(4):
        x = cx - r//2 + i * (r//4)
        pygame.draw.rect(surf, (60, 60, 60), (x, cy + r//2 + 2, 3, 8))
    pygame.draw.line(surf, (240, 240, 235),
                     (int(size*0.15), int(size*0.90)),
                     (int(size*0.85), int(size*0.80)), 10)
    pygame.draw.line(surf, (60, 60, 60),
                     (int(size*0.15), int(size*0.90)),
                     (int(size*0.85), int(size*0.80)), 2)
    return surf


def make_crown_icon(size=90):
    """Корона для экрана победы."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    w, h = size, size
    # основание
    base_y = int(h * 0.72)
    base_h = int(h * 0.20)
    # зубцы
    pts = [
        (int(w*0.10), base_y),
        (int(w*0.10), int(h*0.30)),
        (int(w*0.28), int(h*0.50)),
        (int(w*0.50), int(h*0.18)),
        (int(w*0.72), int(h*0.50)),
        (int(w*0.90), int(h*0.30)),
        (int(w*0.90), base_y),
    ]
    pygame.draw.polygon(surf, (255, 210, 60), pts)
    pygame.draw.polygon(surf, (180, 130, 20), pts, 4)
    # камни
    for cx_, col in [(0.30, (220, 30, 30)), (0.50, (60, 130, 230)),
                     (0.70, (220, 30, 30))]:
        pygame.draw.circle(surf, col,
                           (int(w*cx_), int(h*0.62)), 7)
        pygame.draw.circle(surf, WHITE,
                           (int(w*cx_), int(h*0.62)), 7, 2)
    # база
    pygame.draw.rect(surf, (255, 210, 60),
                     (int(w*0.08), base_y, int(w*0.84), base_h),
                     border_radius=6)
    pygame.draw.rect(surf, (180, 130, 20),
                     (int(w*0.08), base_y, int(w*0.84), base_h),
                     4, border_radius=6)
    return surf


def make_bg_gradient():
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        col = (
            int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
            int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
            int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
        )
        pygame.draw.line(bg, col, (0, y), (WIDTH, y))
    vign = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(60):
        alpha = int(3 + i * 1.2)
        pygame.draw.rect(vign, (0, 0, 0, min(alpha, 90)),
                         (i * 3, i * 3, WIDTH - i * 6, HEIGHT - i * 6),
                         width=6)
    bg.blit(vign, (0, 0))
    for _ in range(1500):
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        c = random.randint(60, 90)
        bg.set_at((x, y), (c, c, c))
    return bg


def make_warning_screen():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / HEIGHT
        col = (int(15*(1-t) + 45*t), int(5*(1-t) + 5*t), int(8*(1-t) + 12*t))
        pygame.draw.line(surf, col, (0, y), (WIDTH, y))
    pygame.draw.rect(surf, (140, 20, 20), (12, 12, WIDTH - 24, HEIGHT - 24),
                     4, border_radius=16)
    pygame.draw.rect(surf, (220, 60, 60), (18, 18, WIDTH - 36, HEIGHT - 36),
                     2, border_radius=14)
    icon = make_warning_icon(150)
    surf.blit(icon, (WIDTH // 2 - icon.get_width() // 2, 45))
    title = font_big.render("ВНИМАНИЕ", True, (255, 60, 60))
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 210))
    lines = [
        ("Эта игра НЕ пропагандирует", WHITE),
        ("и НЕ советует курить.", WHITE),
        ("", WHITE),
        ("Курение вызывает зависимость,", (255, 200, 100)),
        ("вредит лёгким, сердцу", (255, 200, 100)),
        ("и сокращает жизнь.", (255, 200, 100)),
        ("", WHITE),
        ("Игра создана в шуточных", GRAY),
        ("образовательных целях.", GRAY),
    ]
    y = 265
    for text, color in lines:
        if text:
            s = font_small.render(text, True, color)
            surf.blit(s, (WIDTH // 2 - s.get_width() // 2, y))
        y += 25
    healthy = make_lungs_icon(80, healthy=True)
    damaged = make_lungs_icon(80, healthy=False)
    surf.blit(healthy, (WIDTH // 2 - 150, 520))
    surf.blit(damaged, (WIDTH // 2 + 70, 520))
    lbl1 = font_micro.render("ЗДОРОВЫЕ", True, (150, 220, 150))
    lbl2 = font_micro.render("БЕЗ КУРЕНИЯ", True, (150, 220, 150))
    surf.blit(lbl1, (WIDTH // 2 - 150 + 40 - lbl1.get_width() // 2, 610))
    surf.blit(lbl2, (WIDTH // 2 - 150 + 40 - lbl2.get_width() // 2, 625))
    lbl3 = font_micro.render("ТАКИЕ —", True, (220, 80, 80))
    lbl4 = font_micro.render("С КУРЕНИЕМ", True, (220, 80, 80))
    surf.blit(lbl3, (WIDTH // 2 + 70 + 40 - lbl3.get_width() // 2, 610))
    surf.blit(lbl4, (WIDTH // 2 + 70 + 40 - lbl4.get_width() // 2, 625))
    kill = font_med.render("Курение убивает.", True, (255, 50, 50))
    surf.blit(kill, (WIDTH // 2 - kill.get_width() // 2, 665))
    return surf


print("Генерация ресурсов...")
BG_IMG = make_bg_gradient()
WARNING_IMG = make_warning_screen()
SKULL_ICON = make_skull_icon(50)
CROWN_ICON = make_crown_icon(110)
print("Готово!")


# ============================================================
#   СОХРАНЕНИЕ
# ============================================================
SAVE_FILE = "save.json"


def load_save():
    default = {
        "score": 0,
        "total_score": 0,
        "current_pack": 0,
        "upgrades": {"click": 0, "auto": 0},
        "won": False,
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in default.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            return default
    return default


def save_game(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Save error:", e)


def reset_save():
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except Exception:
            pass


state = load_save()
score = float(state["score"])
total_score = float(state["total_score"])
current_pack_idx = int(state.get("current_pack", 0))
upgrades = state["upgrades"]
has_won = bool(state.get("won", False))


# ---------- Параметры ----------
CLICK_UPGRADE_BASE = 50
AUTO_UPGRADE_BASE = 200


def click_upgrade_cost():
    return int(CLICK_UPGRADE_BASE * (1.6 ** upgrades["click"]))


def auto_upgrade_cost():
    return int(AUTO_UPGRADE_BASE * (1.8 ** upgrades["auto"]))


def auto_income_value():
    return upgrades["auto"] * 2


def pack_mult():
    return PACK_TYPES[current_pack_idx]["mult"]


def click_power_value():
    return (1 + upgrades["click"] * 2) * pack_mult()


def pack_unlock_price(idx):
    return PACK_TYPES[idx]["price"]


# ============================================================
#   UI
# ============================================================
floaters = []


def add_floater(x, y, text, color=GOLD):
    floaters.append([x, y, text, 1.0, color])


class Button:
    def __init__(self, rect, text, color, hover_color, action=None, font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.enabled = True
        self.font = font or font_small

    def draw(self, surf):
        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse) and self.enabled
        base = (55, 55, 60) if not self.enabled else (
            self.hover_color if hovered else self.color)
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 110), shadow.get_rect(),
                         border_radius=14)
        surf.blit(shadow, (self.rect.x + 3, self.rect.y + 4))
        pygame.draw.rect(surf, base, self.rect, border_radius=14)
        top_color = tuple(min(255, c + 40) for c in base)
        pygame.draw.rect(surf, top_color,
                         (self.rect.x, self.rect.y, self.rect.w, 6),
                         border_top_left_radius=14, border_top_right_radius=14)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=14)
        col = WHITE if self.enabled else (150, 150, 150)
        t = self.font.render(self.text, True, col)
        surf.blit(t, (self.rect.centerx - t.get_width() // 2,
                      self.rect.centery - t.get_height() // 2))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


def buy_click_upgrade():
    global score
    cost = click_upgrade_cost()
    if score >= cost:
        score -= cost
        upgrades["click"] += 1
        add_floater(WIDTH // 2, HEIGHT // 2 - 100, f"-{cost}", BRIGHT_RED)
        save_state()


def buy_auto_upgrade():
    global score
    cost = auto_upgrade_cost()
    if score >= cost:
        score -= cost
        upgrades["auto"] += 1
        add_floater(WIDTH // 2, HEIGHT // 2 - 100, f"-{cost}", BRIGHT_RED)
        save_state()


def buy_next_pack():
    global score, current_pack_idx
    if current_pack_idx + 1 >= len(PACK_TYPES):
        return
    next_idx = current_pack_idx + 1
    cost = pack_unlock_price(next_idx)
    if score >= cost:
        score -= cost
        current_pack_idx = next_idx
        add_floater(WIDTH // 2, HEIGHT // 2 - 120,
                    f"НОВАЯ ПАЧКА: {PACK_TYPES[next_idx]['name']}", GOLD)
        save_state()


btn_click = Button((30, HEIGHT - 200, WIDTH - 60, 58),
                   "", (70, 100, 160), (90, 130, 200), buy_click_upgrade)
btn_auto = Button((30, HEIGHT - 132, WIDTH - 60, 58),
                  "", (70, 150, 90), (90, 190, 110), buy_auto_upgrade)
btn_next_pack = Button((30, HEIGHT - 268, WIDTH - 60, 58),
                       "", (150, 90, 40), (200, 130, 60),
                       buy_next_pack, font=font_small)


def save_state():
    state["score"] = score
    state["total_score"] = total_score
    state["current_pack"] = current_pack_idx
    state["upgrades"] = upgrades
    state["won"] = has_won
    save_game(state)


# ============================================================
#   ЭКРАН ПРЕДУПРЕЖДЕНИЯ
# ============================================================
def show_warning_screen():
    btn_continue = Button((WIDTH // 2 - 130, HEIGHT - 130, 260, 64),
                          "ПРОДОЛЖИТЬ ▶", (60, 130, 60), (80, 180, 80),
                          None, font=font_med)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_state()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_state()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN, pygame.K_SPACE
            ):
                return
            if btn_continue.handle(event):
                return
        screen.blit(WARNING_IMG, (0, 0))
        btn_continue.draw(screen)
        hint = font_tiny.render(
            "Нажмите кнопку, чтобы продолжить (Enter / Space)",
            True, (180, 180, 180))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 55))
        pygame.display.flip()
        clock.tick(60)


# ============================================================
#   ЭКРАН ПОБЕДЫ
# ============================================================
def show_victory_screen(final_score, final_total):
    """Финальный экран. Ждёт кнопку или Enter/Space."""
    btn_restart = Button((WIDTH // 2 - 140, HEIGHT - 160, 280, 64),
                         "🔁 Начать заново", (150, 60, 60), (200, 90, 90),
                         None, font=font_med)
    btn_exit = Button((WIDTH // 2 - 140, HEIGHT - 85, 280, 58),
                      "Выйти", (60, 60, 70), (90, 90, 110),
                      None, font=font_small)

    t0 = pygame.time.get_ticks()

    while True:
        elapsed = (pygame.time.get_ticks() - t0) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_save()
                    return "restart"
            if btn_restart.handle(event):
                reset_save()
                return "restart"
            if btn_exit.handle(event):
                pygame.quit()
                sys.exit()

        # фон — тёмно-золотой градиент
        for y in range(HEIGHT):
            t = y / HEIGHT
            col = (
                int(20 * (1 - t) + 60 * t),
                int(15 * (1 - t) + 40 * t),
                int(15 * (1 - t) + 15 * t),
            )
            pygame.draw.line(screen, col, (0, y), (WIDTH, y))

        # рамка
        pygame.draw.rect(screen, (180, 140, 40),
                         (12, 12, WIDTH - 24, HEIGHT - 24), 4, border_radius=16)
        pygame.draw.rect(screen, (255, 210, 80),
                         (18, 18, WIDTH - 36, HEIGHT - 36), 2, border_radius=14)

        # Корона (пульсирует)
        pulse = 1.0 + 0.06 * math.sin(elapsed * 3)
        cw = int(CROWN_ICON.get_width() * pulse)
        ch = int(CROWN_ICON.get_height() * pulse)
        crown = pygame.transform.smoothscale(CROWN_ICON, (cw, ch))
        screen.blit(crown, (WIDTH // 2 - cw // 2, 60))

        # Заголовок
        t1 = font_big.render("ПОБЕДА!", True, (255, 215, 80))
        screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 190))

        t2 = font_small.render("Ты прошёл путь от «Примы»", True, WHITE)
        t3 = font_small.render("до PREMIUM BLACK", True, WHITE)
        screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 245))
        screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, 270))

        # Статистика
        box_y = 315
        pygame.draw.rect(screen, (0, 0, 0, 150),
                         (40, box_y, WIDTH - 80, 180), border_radius=14)
        pygame.draw.rect(screen, (200, 160, 60),
                         (40, box_y, WIDTH - 80, 180), 2, border_radius=14)
        stat_lines = [
            ("Всего монет накоплено:", f"{int(final_total):,}".replace(",", " ")),
            ("Финальный баланс:", f"{int(final_score):,}".replace(",", " ")),
            ("Максимум за клик:", f"{int(click_power_value()):,}".replace(",", " ")),
            ("Автодоход:", f"{int(auto_income_value()*pack_mult()):,}/сек".replace(",", " ")),
        ]
        yy = box_y + 18
        for label, val in stat_lines:
            l = font_tiny.render(label, True, LIGHT_GRAY)
            v = font_small.render(val, True, GOLD)
            screen.blit(l, (60, yy))
            screen.blit(v, (WIDTH - 60 - v.get_width(), yy - 2))
            yy += 36

        # Финальное предупреждение
        pygame.draw.rect(screen, (140, 20, 20),
                         (30, 520, WIDTH - 60, 100), border_radius=14)
        pygame.draw.rect(screen, (255, 60, 60),
                         (30, 520, WIDTH - 60, 100), 3, border_radius=14)

        w1 = font_med.render("Но помни:", True, WHITE)
        w2 = font_med.render("Курение убивает.", True, (255, 200, 200))
        w3 = font_tiny.render("Лучшая пачка — та, которую не купил.", True, (255, 220, 220))
        screen.blit(w1, (WIDTH // 2 - w1.get_width() // 2, 535))
        screen.blit(w2, (WIDTH // 2 - w2.get_width() // 2, 568))
        screen.blit(w3, (WIDTH // 2 - w3.get_width() // 2, 600))

        # Кнопки
        btn_restart.draw(screen)
        btn_exit.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
#   ОСНОВНОЙ ЦИКЛ
# ============================================================
def main():
    global score, total_score, current_pack_idx, has_won

    show_warning_screen()

    running = True
    last_auto = pygame.time.get_ticks()

    pack_scale = 1.0
    target_scale = 1.0
    click_anim = 0.0
    idle_time = 0.0
    lid_anim = 0.0
    lid_target = 0.0
    lid_timer = 0.0
    smoke_particles = []
    notif_text = ""
    notif_timer = 0.0
    victory_triggered = False

    pack_center = (WIDTH // 2, 380)

    while running:
        dt = clock.tick(60) / 1000.0
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_state()
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_state()
                    running = False
                if event.key == pygame.K_s:
                    save_state()
                    notif_text = "Игра сохранена"
                    notif_timer = 1.5
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                img = PACK_IMAGES[current_pack_idx]
                rect = img.get_rect(center=pack_center)
                if rect.collidepoint(event.pos):
                    gain = click_power_value()
                    score += gain
                    total_score += gain
                    add_floater(event.pos[0], event.pos[1], f"+{gain}")
                    click_anim = 0.15
                    target_scale = 0.92
                    for _ in range(5):
                        smoke_particles.append({
                            "x": event.pos[0] + random.randint(-30, 30),
                            "y": event.pos[1] + random.randint(-30, 30),
                            "vx": random.uniform(-20, 20),
                            "vy": random.uniform(-55, -25),
                            "life": 1.0,
                            "r": random.randint(6, 15),
                        })

            btn_click.handle(event)
            btn_auto.handle(event)
            btn_next_pack.handle(event)

        # Автодоход
        if now - last_auto >= 1000:
            last_auto = now
            inc = auto_income_value() * pack_mult()
            if inc > 0:
                score += inc
                total_score += inc

        # 🏁 ПРОВЕРКА ФИНАЛА
        if (not victory_triggered
                and current_pack_idx == len(PACK_TYPES) - 1
                and score >= FINAL_TARGET):
            victory_triggered = True
            has_won = True
            save_state()
            result = show_victory_screen(score, total_score)
            if result == "restart":
                # сброс
                score = 0
                total_score = 0
                current_pack_idx = 0
                upgrades["click"] = 0
                upgrades["auto"] = 0
                has_won = False
                victory_triggered = False
                save_state()
                continue

        # Анимации
        idle_time += dt
        if click_anim > 0:
            click_anim -= dt
            if click_anim <= 0:
                target_scale = 1.0
        pack_scale += (target_scale - pack_scale) * min(1, dt * 15)
        if lid_timer > 0:
            lid_timer -= dt
            if lid_timer <= 0:
                lid_target = 0.0
        lid_anim += (lid_target - lid_anim) * min(1, dt * 8)
        if notif_timer > 0:
            notif_timer -= dt

        # ОТРИСОВКА
        screen.blit(BG_IMG, (0, 0))

        top_bar = pygame.Surface((WIDTH, 185), pygame.SRCALPHA)
        top_bar.fill((0, 0, 0, 140))
        screen.blit(top_bar, (0, 0))

        title = font_med.render("CIGARETTE CLICKER", True, GOLD)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 8))

        warn = font_tiny.render("Курение вредит вашему здоровью!", True,
                                (255, 90, 90))
        screen.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 38))

        score_txt = font_huge.render(f"{int(score)}", True, WHITE)
        screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, 58))

        pk = PACK_TYPES[current_pack_idx]
        pack_label = font_small.render(
            f"Пачка: {pk['name']}  ×{pk['mult']}", True, GOLD)
        screen.blit(pack_label, (WIDTH // 2 - pack_label.get_width() // 2, 125))

        rate = font_tiny.render(
            f"+{click_power_value()} за клик  •  +{auto_income_value()*pack_mult()}/сек",
            True, LIGHT_GRAY)
        screen.blit(rate, (WIDTH // 2 - rate.get_width() // 2, 148))

        # 🏁 ПРОГРЕСС-БАР ДО ФИНАЛА
        prog_y = 168
        bar_x, bar_w = 30, WIDTH - 60
        bar_h = 10
        if current_pack_idx == len(PACK_TYPES) - 1:
            progress = min(1.0, score / FINAL_TARGET)
        else:
            # прогресс по количеству пачек
            progress = current_pack_idx / (len(PACK_TYPES) - 1)
        pygame.draw.rect(screen, (50, 50, 60),
                         (bar_x, prog_y, bar_w, bar_h), border_radius=5)
        pygame.draw.rect(screen, GOLD,
                         (bar_x, prog_y, int(bar_w * progress), bar_h),
                         border_radius=5)
        pygame.draw.rect(screen, BLACK,
                         (bar_x, prog_y, bar_w, bar_h), 2, border_radius=5)

        if current_pack_idx == len(PACK_TYPES) - 1:
            goal_txt = font_tiny.render(
                f"ФИНАЛ: {int(score):,} / {FINAL_TARGET:,}".replace(",", " "),
                True, GOLD)
        else:
            goal_txt = font_tiny.render(
                f"Прогресс до финала: {current_pack_idx}/{len(PACK_TYPES)-1} пачек",
                True, LIGHT_GRAY)
        screen.blit(goal_txt, (WIDTH // 2 - goal_txt.get_width() // 2,
                               prog_y + 14))

        # ПАЧКА
        wobble_x = math.sin(idle_time * 1.8) * 4
        wobble_y = math.sin(idle_time * 2.4) * 3
        base_img = (PACK_IMAGES_OPEN[current_pack_idx]
                    if lid_anim > 0.5 else PACK_IMAGES[current_pack_idx])
        w = int(base_img.get_width() * pack_scale)
        h = int(base_img.get_height() * pack_scale)
        scaled = pygame.transform.smoothscale(base_img, (w, h))

        shadow_w = int(w * 0.8)
        shadow_h = 22
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120),
                            (0, 0, shadow_w, shadow_h))
        sx = pack_center[0] - shadow_w // 2 + wobble_x
        sy = pack_center[1] + h // 2 - 6 + wobble_y
        screen.blit(shadow_surf, (sx, sy))

        rect = scaled.get_rect(
            center=(pack_center[0] + wobble_x, pack_center[1] + wobble_y))
        screen.blit(scaled, rect)

        # ДЫМ
        for p in smoke_particles[:]:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 10 * dt
            p["life"] -= dt * 1.2
            if p["life"] <= 0:
                smoke_particles.remove(p)
                continue
            alpha = int(120 * max(0, p["life"]))
            rad = int(p["r"] * (1.6 - p["life"]))
            if rad > 0:
                s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (200, 200, 200, alpha), (rad, rad), rad)
                screen.blit(s, (int(p["x"] - rad), int(p["y"] - rad)))

        # ЦИФРЫ
        for f in floaters[:]:
            f[1] -= 70 * dt
            f[3] -= dt * 1.2
            if f[3] <= 0:
                floaters.remove(f)
                continue
            alpha = max(0, min(255, int(f[3] * 255)))
            txt = font_med.render(f[2], True, f[4])
            txt.set_alpha(alpha)
            screen.blit(txt, (f[0] - txt.get_width() // 2, int(f[1])))

        # КНОПКИ
        if current_pack_idx + 1 < len(PACK_TYPES):
            nxt = PACK_TYPES[current_pack_idx + 1]
            cost = pack_unlock_price(current_pack_idx + 1)
            btn_next_pack.text = f"Новая пачка: {nxt['name']} ({cost})"
            btn_next_pack.enabled = score >= cost
            btn_next_pack.draw(screen)

        btn_click.text = f"Улучшить клик ({click_upgrade_cost()})"
        btn_auto.text = f"Автоклик ({auto_upgrade_cost()})"
        btn_click.enabled = score >= click_upgrade_cost()
        btn_auto.enabled = score >= auto_upgrade_cost()
        btn_click.draw(screen)
        btn_auto.draw(screen)

        foot = font_tiny.render("Игра-шутка. Курение убивает.", True,
                                (180, 100, 100))
        screen.blit(foot, (WIDTH // 2 - foot.get_width() // 2, HEIGHT - 30))

        if notif_timer > 0:
            n = font_small.render(notif_text, True, GOLD)
            bg_n = pygame.Surface((n.get_width() + 30, n.get_height() + 16),
                                  pygame.SRCALPHA)
            bg_n.fill((0, 0, 0, 190))
            screen.blit(bg_n, (WIDTH // 2 - bg_n.get_width() // 2, HEIGHT - 320))
            screen.blit(n, (WIDTH // 2 - n.get_width() // 2, HEIGHT - 312))

        pygame.display.flip()

    save_state()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()