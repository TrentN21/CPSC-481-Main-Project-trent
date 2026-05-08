import math
import random
import pygame

import board as game
from constants import (
    W, H,
    C_BG, C_BOARD, C_PIT_EMPTY, C_PIT_HOV, C_STONE, C_STONE_SH,
    C_MANCALA, C_TEXT, C_ACCENT, C_PLAYER, C_OPONENT, C_BANNER_BG,
    BOARD_X, BOARD_Y, BOARD_W, BOARD_H,
    MAN_W, MAN_H, COL_W, PIT_R,
)


# Fonts are injected at startup by main.py
FONT_LG = FONT_MD = FONT_SM = FONT_TINY = None

def set_fonts(lg, md, sm, tiny):
    global FONT_LG, FONT_MD, FONT_SM, FONT_TINY
    FONT_LG, FONT_MD, FONT_SM, FONT_TINY = lg, md, sm, tiny


# ── Helpers ───────────────────────────────────────────────────────────────────
def pit_center(index):
    """Return (cx, cy) for a pit circle."""
    if index == 6:
        return (BOARD_X + BOARD_W - MAN_W // 2, BOARD_Y + BOARD_H // 2)
    if index == 13:
        return (BOARD_X + MAN_W // 2, BOARD_Y + BOARD_H // 2)
    x_start = BOARD_X + MAN_W + 20  # PIT_GAP = 20
    if index < 6:
        cx = x_start + index * COL_W + COL_W // 2
        cy = BOARD_Y + BOARD_H * 3 // 4
    else:
        slot = index - 7
        cx = x_start + (5 - slot) * COL_W + COL_W // 2
        cy = BOARD_Y + BOARD_H // 4
    return (cx, cy)


def draw_rounded_rect(surf, color, rect, radius=12):
    pygame.draw.rect(surf, color, rect, border_radius=radius)


# ── Pit / Mancala ─────────────────────────────────────────────────────────────
def draw_pit(screen, index, stones, is_mancala=False, highlight=False):
    cx, cy = pit_center(index)
    if is_mancala:
        rw, rh = MAN_W - 10, MAN_H - 20
        r = pygame.Rect(cx - rw // 2, cy - rh // 2, rw, rh)
        draw_rounded_rect(screen, C_MANCALA, r, 18)
        pygame.draw.rect(screen, C_ACCENT, r, 2, border_radius=18)

        top_count = stones // 2
        bottom_count = stones - top_count
        spread_r = rw // 2 - 12
        offset_y = rh // 4 + 5 

        if top_count > 0:
            draw_stones_in_pit(screen, cx, cy - offset_y, spread_r, top_count)
        if bottom_count > 0:
            draw_stones_in_pit(screen, cx, cy + offset_y, spread_r, bottom_count)
        
        txt = FONT_LG.render(str(stones), True, C_TEXT)
        screen.blit(txt, txt.get_rect(center=(cx, cy)))
        lbl = FONT_TINY.render("PLAYER" if index == 6 else "AI", True, C_ACCENT)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy + rh // 2 - 14)))
    else:
        color = C_PIT_HOV if highlight else C_PIT_EMPTY
        pygame.draw.circle(screen, color, (cx, cy), PIT_R)
        pygame.draw.circle(screen, C_ACCENT, (cx, cy), PIT_R, 2)
        draw_stones_in_pit(screen, cx, cy, PIT_R - 8, stones)

        count_txt = FONT_SM.render(str(stones), True, C_TEXT)
        screen.blit(count_txt, count_txt.get_rect(center=(cx, cy - PIT_R - 15)))


def draw_stones_in_pit(screen, cx, cy, area_r, count):
    if count == 0:
        return
    stone_r = max(3, min(10, area_r // (math.ceil(math.sqrt(count)) + 1)))
    positions = []
    attempts  = 0
    rng = random.Random(count * 1000)
    while len(positions) < count and attempts < count * 50:
        attempts += 1
        angle = rng.uniform(0, 2 * math.pi)
        dist  = rng.uniform(0, area_r - stone_r)
        px = int(cx + dist * math.cos(angle))
        py = int(cy + dist * math.sin(angle))
        ok = True
        for qx, qy in positions:
            if math.hypot(px - qx, py - qy) < stone_r * 2.2:
                ok = False; break
        if ok:
            positions.append((px, py))
    if len(positions) < count:
        positions = []
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
        for r in range(rows):
            for c in range(cols):
                if len(positions) >= count:
                    break
                px = int(cx - (cols - 1) * stone_r * 1.4 / 2 + c * stone_r * 1.4)
                py = int(cy - (rows - 1) * stone_r * 1.4 / 2 + r * stone_r * 1.4)
                positions.append((px, py))
    for px, py in positions[:count]:
        pygame.draw.circle(screen, C_STONE_SH, (px + 1, py + 2), stone_r)
        pygame.draw.circle(screen, C_STONE,    (px,     py),     stone_r)


# ── Screens ───────────────────────────────────────────────────────────────────
def draw_board(screen, board, turn, phase, hover_pit):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)
    draw_rounded_rect(screen, C_BOARD, board_rect, 20)
    pygame.draw.rect(screen, C_ACCENT, board_rect, 3, border_radius=20)

    p_lbl = FONT_SM.render("YOUR SIDE", True, C_PLAYER)
    screen.blit(p_lbl, p_lbl.get_rect(center=(W // 2, BOARD_Y + BOARD_H + 20)))
    o_lbl = FONT_SM.render("AI SIDE", True, C_OPONENT)
    screen.blit(o_lbl, o_lbl.get_rect(center=(W // 2, BOARD_Y - 20)))

    if phase == "playing":
        if turn == 0:
            ind = FONT_SM.render("▶ Your turn", True, C_PLAYER)
        else:
            ind = FONT_SM.render("⏳ AI thinking…", True, C_OPONENT)
        screen.blit(ind, ind.get_rect(topright=(W - 20, 12)))

    draw_pit(screen, 6,  board[6],  is_mancala=True)
    draw_pit(screen, 13, board[13], is_mancala=True)

    for i in range(6):
        hi = (i == hover_pit and turn == 0 and phase == "playing" and board[i] > 0)
        draw_pit(screen, i, board[i], highlight=hi)
    for i in range(7, 13):
        draw_pit(screen, i, board[i])

    for i in range(6):
        cx, cy = pit_center(i)
        lbl = FONT_TINY.render(str(i + 1), True, C_ACCENT)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy + PIT_R + 8)))


def draw_menu(screen, start_btn, diff_btn, difficulty, diff_list):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 300, 400
    bx = (W - box_w) // 2
    by = (H - box_h) // 2
    draw_rounded_rect(screen, C_BANNER_BG, (bx, by, box_w, box_h), 20)
    pygame.draw.rect(screen, C_ACCENT, (bx, by, box_w, box_h), 3, border_radius=20)

    title = FONT_LG.render("Mancala", True, C_ACCENT)
    screen.blit(title, title.get_rect(center=(W // 2, H // 4)))

    start_btn.draw()
    diff_btn.draw()

    text = FONT_MD.render("Difficulty: " + str(diff_list[difficulty]), True, C_STONE_SH)
    screen.blit(text, text.get_rect(center=(W // 2, H // 2 + 100)))


def draw_game_over(screen, winner_text):
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    screen.blit(overlay, (0, 0))

    box_w, box_h = 460, 220
    bx = (W - box_w) // 2
    by = (H - box_h) // 2
    draw_rounded_rect(screen, C_BANNER_BG, (bx, by, box_w, box_h), 20)
    pygame.draw.rect(screen, C_ACCENT, (bx, by, box_w, box_h), 3, border_radius=20)

    title = FONT_LG.render("Game Over", True, C_ACCENT)
    screen.blit(title, title.get_rect(center=(W // 2, by + 55)))

    result = FONT_MD.render(winner_text, True, C_TEXT)
    screen.blit(result, result.get_rect(center=(W // 2, by + 115)))

    restart = FONT_SM.render("Press R to restart  |  Q to quit", True, C_STONE_SH)
    screen.blit(restart, restart.get_rect(center=(W // 2, by + 170)))
