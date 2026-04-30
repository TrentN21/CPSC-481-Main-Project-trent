import random
from constants import AI_THINK_DELAY, ANIM_DELAY

# ── Game State ────────────────────────────────────────────────────────────────
board        = []
turn         = 0          # 0 = player, 1 = opponent
anim_queue   = []
anim_timer   = 0
phase        = "menu"     # "playing" | "game_over"
winner_text  = ""
hover_pit    = -1
ai_delay_timer = 0
diff_list    = ["Easy", "Medium", "Hard"]
difficulty   = 1


def new_board():
    b = [4] * 14
    b[6]  = 0
    b[13] = 0
    return b


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


def schedule_ai():
    global ai_delay_timer
    ai_delay_timer = AI_THINK_DELAY


# ── AI ────────────────────────────────────────────────────────────────────────
def ai_pick():
    if difficulty == 0:
        valid = [i for i in range(7, 13) if board[i] > 0]
        return random.choice(valid) if valid else -1
    elif difficulty == 1:
        # Priority 1: move that lands in mancala (free turn)
        for i in range(7, 13):
            if board[i] > 0 and (i + board[i]) % 14 == 13:
                return i
        # Priority 2: capture
        for i in range(7, 13):
            if board[i] > 0:
                end = (i + board[i]) % 14
                if 7 <= end <= 12 and board[end] == 0 and board[12 - end] > 0:
                    return i
        # Priority 3: pit with most stones
        best, best_val = -1, -1
        for i in range(7, 13):
            if board[i] > best_val:
                best_val, best = board[i], i
        if best == -1 or best_val == 0:
            valid = [i for i in range(7, 13) if board[i] > 0]
            return random.choice(valid) if valid else -1
        return best
    else:
        # Placeholder for minimax
        pass


# ── Action Logic ──────────────────────────────────────────────────────────────
def enqueue_action(start, side):
    stones = board[start]
    if stones == 0:
        return False
    board[start] = 0
    anim_queue.append(("empty", start))

    counter = start
    for _ in range(stones):
        counter += 1
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
                turn = side
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
