import pygame
import random
import sys
import math

pygame.init()

# ── Display ──────────────────────────────────────────────────────────────────
W, H = 900, 520
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Mancala")
clock = pygame.time.Clock()

# ── Palette ───────────────────────────────────────────────────────────────────
C_BG        = (42,  28,  18)   # deep walnut
C_BOARD     = (101, 67,  33)   # medium wood
C_PIT_EMPTY = (75,  46,  22)   # dark wood hollow
C_PIT_HOV   = (130, 90,  45)   # highlight hover
C_STONE     = (220, 185, 120)  # warm gold stone
C_STONE_SH  = (160, 120,  60)  # stone shadow
C_MANCALA   = (55,  35,  15)   # mancala well
C_TEXT      = (245, 230, 190)  # cream text
C_ACCENT    = (210, 140,  50)  # amber accent
C_PLAYER    = (100, 180, 100)  # green player indicator
C_OPONENT   = (180, 100, 100)  # red opponent indicator
C_BANNER_BG = (30,  18,   8)   # dark overlay

# ── Fonts ─────────────────────────────────────────────────────────────────────
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

# ── Board Layout ──────────────────────────────────────────────────────────────
#  Pits 0-5   = player bottom row  (left→right)
#  Pit  6     = player mancala     (right)
#  Pits 7-12  = opponent top row   (right→left, i.e. pit 7 is above pit 5)
#  Pit  13    = opponent mancala   (left)

PIT_R     = 42          # pit circle radius
PIT_GAP   = 20          # gap between pits
BOARD_X   = 60          # left edge of board
BOARD_Y   = 80          # top edge of board
BOARD_W   = W - 120
BOARD_H   = H - 160
MAN_W     = 75          # mancala well width
MAN_H     = BOARD_H
PIT_AREA_W = BOARD_W - 2 * (MAN_W + PIT_GAP)
COL_W      = PIT_AREA_W // 6

class Button:
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.button = pygame.rect.Rect(self.pos[0], self.pos[1], 160, 60)
    def draw(self):
        btn = pygame.draw.rect(screen, C_ACCENT, self.button, 3, border_radius=20)
        text = FONT_MD.render(self.text, True, C_STONE_SH)
        screen.blit(text, text.get_rect(center=self.button.center))
    def collidepoint(self, point):
        return self.button.collidepoint(point)

def pit_center(index):
    """Return (cx, cy) for a pit circle."""
    if index == 6:          # player mancala (right)
        return (BOARD_X + BOARD_W - MAN_W // 2, BOARD_Y + BOARD_H // 2)
    if index == 13:         # opponent mancala (left)
        return (BOARD_X + MAN_W // 2, BOARD_Y + BOARD_H // 2)
    x_start = BOARD_X + MAN_W + PIT_GAP
    if index < 6:           # bottom row, left → right
        cx = x_start + index * COL_W + COL_W // 2
        cy = BOARD_Y + BOARD_H * 3 // 4
    else:                   # top row, right → left  (pit 7 above pit 5)
        slot = index - 7    # 0..5
        cx = x_start + (5 - slot) * COL_W + COL_W // 2
        cy = BOARD_Y + BOARD_H // 4
    return (cx, cy)

# ── Game State ─────────────────────────────────────────────────────────────────
def new_board():
    b = [4] * 14
    b[6]  = 0
    b[13] = 0
    return b

board = new_board()

# Turn: 0 = player, 1 = opponent
turn = 0

# Animation queue: list of (pit_index, delta) to apply one at a time
anim_queue = []
anim_timer  = 0
ANIM_DELAY  = 400          # ms per stone drop

phase = "menu"          # "playing" | "game_over"
winner_text = ""
hover_pit   = -1

diff_list = ["Easy", "Medium", "Hard"]
difficulty  = 1   

start_btn = Button("Start", (W // 2 - 80, H // 2 - 80))
diff_btn = Button("Difficulty", (W // 2 - 80, H // 2 ))

# ── AI ────────────────────────────────────────────────────────────────────────
def ai_pick():
    if difficulty == 0:
        #random choice among valid moves
        valid = [i for i in range(7, 13) if board[i] > 0]
        return random.choice(valid) if valid else -1
    elif difficulty == 1:
        """Simple scoring AI for opponent (pits 7-12)."""
        # Priority 1: move that lands in mancala (free turn)
        for i in range(7, 13):
            if board[i] > 0 and (i + board[i]) % 14 == 13:
                return i
        # Priority 2: capture (land on empty pit on own side, opposite has stones)
        for i in range(7, 13):
            if board[i] > 0:
                end = (i + board[i]) % 14
                if 7 <= end <= 12 and board[end] == 0 and board[12 - end] > 0:
                    return i
        # Priority 3: pick the pit with the most stones
        best, best_val = -1, -1
        for i in range(7, 13):
            if board[i] > best_val:
                best_val, best = board[i], i
        if best == -1 or best_val == 0:
            # fallback random
            valid = [i for i in range(7, 13) if board[i] > 0]
            return random.choice(valid) if valid else -1
        return best
    else:
        #for min max
        pass

# ── Action Logic (builds animation queue) ────────────────────────────────────
def enqueue_action(start, side):
    """
    Walk through the move, pushing (pit, +1) entries into anim_queue.
    Also handles capture and end-turn / free-turn logic.
    Returns True if the player gets a free turn.
    """
    stones = board[start]
    if stones == 0:
        return False
    board[start] = 0
    anim_queue.append(("empty", start))

    counter = start
    for _ in range(stones):
        counter += 1
        # Skip opponent's mancala
        if side == 0 and counter == 13:
            counter += 1
        elif side == 1 and counter == 6:
            counter += 1
        counter %= 14
        anim_queue.append(("add", counter))

    # Capture check
    if side == 0 and 0 <= counter <= 5 and board[counter] == 0:
        opp = 12 - counter
        if board[opp] > 0:
            anim_queue.append(("capture_player", counter, opp))
    elif side == 1 and 7 <= counter <= 12 and board[counter] == 0:
        opp = 12 - counter
        if board[opp] > 0:
            anim_queue.append(("capture_opp", counter, opp))

    free_turn = (side == 0 and counter == 6) or (side == 1 and counter == 13)
    anim_queue.append(("end_move", side, free_turn))
    return free_turn

def apply_event(ev):
    """Apply a single queued animation event to the board."""
    global turn, phase, winner_text
    kind = ev[0]
    if kind == "empty":
        board[ev[1]] = 0
    elif kind == "add":
        board[ev[1]] += 1
    elif kind == "capture_player":
        pit, opp = ev[1], ev[2]
        board[6] += board[opp] + board[pit]
        board[opp] = 0
        board[pit]  = 0
    elif kind == "capture_opp":
        pit, opp = ev[1], ev[2]
        board[13] += board[opp] + board[pit]
        board[opp] = 0
        board[pit]  = 0
    elif kind == "end_move":
        side, free_turn = ev[1], ev[2]
        check_end()
        if phase == "playing":
            if free_turn:
                turn = side          # same player goes again
                if turn == 1:
                    schedule_ai()
            else:
                turn = 1 - side
                if turn == 1:
                    schedule_ai()

def check_end():
    global phase, winner_text, board
    player_empty = all(board[i] == 0 for i in range(6))
    opp_empty    = all(board[i] == 0 for i in range(7, 13))
    if player_empty or opp_empty:
        # Sweep remaining stones
        for i in range(6):
            board[6]  += board[i]; board[i] = 0
        for i in range(7, 13):
            board[13] += board[i]; board[i] = 0
        phase = "game_over"
        if board[6] > board[13]:
            winner_text = f"You win!  {board[6]} – {board[13]}"
        elif board[13] > board[6]:
            winner_text = f"AI wins!  {board[13]} – {board[6]}"
        else:
            winner_text = f"It's a tie!  {board[6]} – {board[13]}"

ai_delay_timer = 0
AI_THINK_DELAY = 600   # ms before AI "thinks"

def schedule_ai():
    global ai_delay_timer
    ai_delay_timer = AI_THINK_DELAY

# ── Drawing ───────────────────────────────────────────────────────────────────
def draw_rounded_rect(surf, color, rect, radius=12):
    pygame.draw.rect(surf, color, rect, border_radius=radius)

def draw_pit(index, stones, is_mancala=False, highlight=False):
    cx, cy = pit_center(index)
    if is_mancala:
        rw, rh = MAN_W - 10, MAN_H - 20
        r = pygame.Rect(cx - rw//2, cy - rh//2, rw, rh)
        draw_rounded_rect(screen, C_MANCALA, r, 18)
        pygame.draw.rect(screen, C_ACCENT, r, 2, border_radius=18)
        # Score
        txt = FONT_LG.render(str(stones), True, C_TEXT)
        screen.blit(txt, txt.get_rect(center=(cx, cy)))
        # Label
        lbl = FONT_TINY.render("PLAYER" if index == 6 else "AI", True, C_ACCENT)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy + rh//2 - 14)))
    else:
        color = C_PIT_HOV if highlight else C_PIT_EMPTY
        pygame.draw.circle(screen, color, (cx, cy), PIT_R)
        pygame.draw.circle(screen, C_ACCENT, (cx, cy), PIT_R, 2)
        # Draw stones as small circles arranged inside pit
        draw_stones_in_pit(cx, cy, PIT_R - 8, stones)

def draw_stones_in_pit(cx, cy, area_r, count):
    if count == 0:
        return
    stone_r = max(3, min(10, area_r // (math.ceil(math.sqrt(count)) + 1)))
    positions = []
    attempts  = 0
    rng = random.Random(count * 1000)   # deterministic per count
    while len(positions) < count and attempts < count * 50:
        attempts += 1
        angle = rng.uniform(0, 2 * math.pi)
        dist  = rng.uniform(0, area_r - stone_r)
        px = int(cx + dist * math.cos(angle))
        py = int(cy + dist * math.sin(angle))
        # Check no overlap
        ok = True
        for qx, qy in positions:
            if math.hypot(px - qx, py - qy) < stone_r * 2.2:
                ok = False; break
        if ok:
            positions.append((px, py))
    # Fallback: grid
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

def draw_menu():
    global phase, difficulty, diff_list 
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

def draw_board():
    # Board background
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_W, BOARD_H)
    draw_rounded_rect(screen, C_BOARD, board_rect, 20)
    pygame.draw.rect(screen, C_ACCENT, board_rect, 3, border_radius=20)

    # Side labels
    p_lbl = FONT_SM.render("YOUR SIDE", True, C_PLAYER)
    screen.blit(p_lbl, p_lbl.get_rect(center=(W // 2, BOARD_Y + BOARD_H + 20)))
    o_lbl = FONT_SM.render("AI SIDE", True, C_OPONENT)
    screen.blit(o_lbl, o_lbl.get_rect(center=(W // 2, BOARD_Y - 20)))

    # Turn indicator
    if phase == "playing":
        if turn == 0:
            ind = FONT_SM.render("▶ Your turn", True, C_PLAYER)
        else:
            ind = FONT_SM.render("⏳ AI thinking…", True, C_OPONENT)
        screen.blit(ind, ind.get_rect(topright=(W - 20, 12)))

    # Mancalas
    draw_pit(6,  board[6],  is_mancala=True)
    draw_pit(13, board[13], is_mancala=True)

    # Pits 0-5 and 7-12
    for i in range(6):
        hi = (i == hover_pit and turn == 0 and phase == "playing" and board[i] > 0)
        draw_pit(i, board[i], highlight=hi)
    for i in range(7, 13):
        draw_pit(i, board[i])

    # Pit number hints (small, below player pits)
    for i in range(6):
        cx, cy = pit_center(i)
        lbl = FONT_TINY.render(str(i + 1), True, C_ACCENT)
        screen.blit(lbl, lbl.get_rect(center=(cx, cy + PIT_R + 8)))

def draw_game_over():
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

# ── Main Loop ─────────────────────────────────────────────────────────────────
def reset():
    global board, turn, anim_queue, anim_timer, phase, winner_text, hover_pit, ai_delay_timer
    board          = new_board()
    turn           = 0
    anim_queue     = []
    anim_timer     = 0
    phase          = "playing"
    winner_text    = ""
    hover_pit      = -1
    ai_delay_timer = 0

while True:
    dt = clock.tick(60)

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_btn.collidepoint(pygame.mouse.get_pos()):
                phase = "playing"
            elif diff_btn.collidepoint(pygame.mouse.get_pos()):
                difficulty = (difficulty + 1) % len(diff_list)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit(); sys.exit()
            if event.key == pygame.K_r:
                reset()
            if event.key == pygame.K_ESCAPE:
                if phase == "playing":
                    phase = "menu"
                elif phase == "menu":
                    phase = "playing"

        if phase == "playing" and not anim_queue:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if turn == 0:
                    mx, my = event.pos
                    for i in range(6):
                        if board[i] > 0:
                            cx, cy = pit_center(i)
                            if math.hypot(mx - cx, my - cy) <= PIT_R:
                                enqueue_action(i, 0)
                                break

    # ── Hover ──────────────────────────────────────────────────────────────────
    if phase == "playing" and turn == 0 and not anim_queue:
        mx, my = pygame.mouse.get_pos()
        hover_pit = -1
        for i in range(6):
            if board[i] > 0:
                cx, cy = pit_center(i)
                if math.hypot(mx - cx, my - cy) <= PIT_R:
                    hover_pit = i; break
    else:
        hover_pit = -1

    # ── AI Trigger ────────────────────────────────────────────────────────────
    if phase == "playing" and turn == 1 and not anim_queue and ai_delay_timer > 0:
        ai_delay_timer -= dt
        if ai_delay_timer <= 0:
            choice = ai_pick()
            if choice != -1:
                enqueue_action(choice, 1)

    # ── Process Animation Queue ───────────────────────────────────────────────
    if anim_queue:
        anim_timer += dt
        if anim_timer >= ANIM_DELAY:
            anim_timer = 0
            ev = anim_queue.pop(0)
            apply_event(ev)

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill(C_BG)
    draw_board()

    menu_text = FONT_SM.render("press esc for menu", True, C_ACCENT)
    screen.blit(menu_text, menu_text.get_rect(topleft=(20, 12)))

    if phase == "menu":
        draw_menu()

    
    if phase == "game_over":
        draw_game_over()

    pygame.display.flip()