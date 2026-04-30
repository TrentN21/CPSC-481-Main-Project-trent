import pygame

# ── Display ───────────────────────────────────────────────────────────────────
W, H = 900, 520

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG        = (42,  28,  18)
C_BOARD     = (101, 67,  33)
C_PIT_EMPTY = (75,  46,  22)
C_PIT_HOV   = (130, 90,  45)
C_STONE     = (220, 185, 120)
C_STONE_SH  = (160, 120,  60)
C_MANCALA   = (55,  35,  15)
C_TEXT      = (245, 230, 190)
C_ACCENT    = (210, 140,  50)
C_PLAYER    = (100, 180, 100)
C_OPONENT   = (180, 100, 100)
C_BANNER_BG = (30,  18,   8)

# ── Fonts ─────────────────────────────────────────────────────────────────────
def init_fonts():
    try:
        FONT_LG   = pygame.font.SysFont("Georgia", 42, bold=True)
        FONT_MD   = pygame.font.SysFont("Georgia", 28)
        FONT_SM   = pygame.font.SysFont("Georgia", 20)
        FONT_TINY = pygame.font.SysFont("Georgia", 15)
    except:
        FONT_LG   = pygame.font.SysFont(None, 42)
        FONT_MD   = pygame.font.SysFont(None, 28)
        FONT_SM   = pygame.font.SysFont(None, 20)
        FONT_TINY = pygame.font.SysFont(None, 15)
    return FONT_LG, FONT_MD, FONT_SM, FONT_TINY

# ── Board Layout ──────────────────────────────────────────────────────────────
PIT_R      = 42
PIT_GAP    = 20
BOARD_X    = 60
BOARD_Y    = 80
BOARD_W    = W - 120
BOARD_H    = H - 160
MAN_W      = 75
MAN_H      = BOARD_H
PIT_AREA_W = BOARD_W - 2 * (MAN_W + PIT_GAP)
COL_W      = PIT_AREA_W // 6

ANIM_DELAY    = 400   # ms per stone drop
AI_THINK_DELAY = 600  # ms before AI "thinks"
