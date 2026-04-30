import math
import sys

import pygame

import board as game
import renderer
from constants import (
    W, H, C_BG, C_ACCENT, ANIM_DELAY,
    init_fonts,
)

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mancala")
clock = pygame.time.Clock()

FONT_LG, FONT_MD, FONT_SM, FONT_TINY = init_fonts()
renderer.set_fonts(FONT_LG, FONT_MD, FONT_SM, FONT_TINY)

# ── UI Buttons ────────────────────────────────────────────────────────────────
class Button:
    def __init__(self, text, pos):
        self.text   = text
        self.pos    = pos
        self.button = pygame.rect.Rect(self.pos[0], self.pos[1], 160, 60)

    def draw(self):
        pygame.draw.rect(screen, C_ACCENT, self.button, 3, border_radius=20)
        text = FONT_MD.render(self.text, True, (160, 120, 60))
        screen.blit(text, text.get_rect(center=self.button.center))

    def collidepoint(self, point):
        return self.button.collidepoint(point)


start_btn = Button("Start",      (W // 2 - 80, H // 2 - 80))
diff_btn  = Button("Difficulty", (W // 2 - 80, H // 2))

# Seed the game board
game.board = game.new_board()

# ── Main Loop ─────────────────────────────────────────────────────────────────
while True:
    dt = clock.tick(60)

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game.phase == "menu":
                if start_btn.collidepoint(pygame.mouse.get_pos()):
                    game.phase = "playing"
                elif diff_btn.collidepoint(pygame.mouse.get_pos()):
                    game.difficulty = (game.difficulty + 1) % len(game.diff_list)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_r:
                game.reset()
            if event.key == pygame.K_ESCAPE:
                if game.phase == "playing":
                    game.phase = "menu"
                elif game.phase == "menu":
                    game.phase = "playing"

        if game.phase == "playing" and not game.anim_queue:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.turn == 0:
                    mx, my = event.pos
                    for i in range(6):
                        if game.board[i] > 0:
                            cx, cy = renderer.pit_center(i)
                            if math.hypot(mx - cx, my - cy) <= 42:  # PIT_R
                                game.enqueue_action(i, 0)
                                break

    # ── Hover ─────────────────────────────────────────────────────────────────
    if game.phase == "playing" and game.turn == 0 and not game.anim_queue:
        mx, my = pygame.mouse.get_pos()
        game.hover_pit = -1
        for i in range(6):
            if game.board[i] > 0:
                cx, cy = renderer.pit_center(i)
                if math.hypot(mx - cx, my - cy) <= 42:
                    game.hover_pit = i; break
    else:
        game.hover_pit = -1

    # ── AI Trigger ────────────────────────────────────────────────────────────
    if game.phase == "playing" and game.turn == 1 and not game.anim_queue and game.ai_delay_timer > 0:
        game.ai_delay_timer -= dt
        if game.ai_delay_timer <= 0:
            choice = game.ai_pick()
            if choice != -1:
                game.enqueue_action(choice, 1)

    # ── Process Animation Queue ───────────────────────────────────────────────
    if game.anim_queue:
        game.anim_timer += dt
        if game.anim_timer >= ANIM_DELAY:
            game.anim_timer = 0
            ev = game.anim_queue.pop(0)
            game.apply_event(ev)

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill(C_BG)
    renderer.draw_board(screen, game.board, game.turn, game.phase, game.hover_pit)

    menu_text = FONT_SM.render("press esc for menu", True, C_ACCENT)
    screen.blit(menu_text, menu_text.get_rect(topleft=(20, 12)))

    if game.phase == "menu":
        renderer.draw_menu(screen, start_btn, diff_btn, game.difficulty, game.diff_list)

    if game.phase == "game_over":
        renderer.draw_game_over(screen, game.winner_text)

    pygame.display.flip()
