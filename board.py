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
        # Minimax with alpha-beta pruning (AI = maximizer, side 1)
        _, best_pit = alphabeta(board[:], depth=7, alpha=float('-inf'), beta=float('inf'), is_maximizing=True)
        return best_pit if best_pit != -1 else -1


# ── Minimax helpers ───────────────────────────────────────────────────────────
def sim_move(b, pit, side):
    """
    Apply a move to board copy `b` for `side` (0=player, 1=AI).
    Returns (new_board, free_turn).
    """
    stones = b[pit]
    if stones == 0:
        return b, False
    b = b[:]
    b[pit] = 0
    counter = pit
    for _ in range(stones):
        counter += 1
        if side == 0 and counter == 13:
            counter += 1
        elif side == 1 and counter == 6:
            counter += 1
        counter %= 14
        b[counter] += 1

    # Capture
    if side == 0 and 0 <= counter <= 5 and b[counter] == 1:
        opp = 12 - counter
        if b[opp] > 0:
            b[6] += b[opp] + b[counter]
            b[opp] = 0
            b[counter] = 0
    elif side == 1 and 7 <= counter <= 12 and b[counter] == 1:
        opp = 12 - counter
        if b[opp] > 0:
            b[13] += b[opp] + b[counter]
            b[opp] = 0
            b[counter] = 0

    free_turn = (side == 0 and counter == 6) or (side == 1 and counter == 13)
    return b, free_turn


def sim_check_end(b):
    """Sweep remaining stones and return terminal board, or None if not terminal."""
    player_empty = all(b[i] == 0 for i in range(6))
    opp_empty    = all(b[i] == 0 for i in range(7, 13))
    if not (player_empty or opp_empty):
        return None
    b = b[:]
    for i in range(6):
        b[6]  += b[i]; b[i] = 0
    for i in range(7, 13):
        b[13] += b[i]; b[i] = 0
    return b


def heuristic(b):
    """Score from AI's perspective: mancala diff + positional bonuses."""
    score = (b[13] - b[6]) * 2  # mancala stones weighted heavily

    # Bonus for free-turn opportunities
    for i in range(7, 13):
        if b[i] > 0 and (i + b[i]) % 14 == 13:
            score += 3
    for i in range(6):
        if b[i] > 0 and (i + b[i]) % 14 == 6:
            score -= 3

    # Bonus for capture opportunities
    for i in range(7, 13):
        if b[i] > 0:
            end = (i + b[i]) % 14
            if 7 <= end <= 12 and b[end] == 0 and b[12 - end] > 0:
                score += b[12 - end]
    for i in range(6):
        if b[i] > 0:
            end = (i + b[i]) % 14
            if 0 <= end <= 5 and b[end] == 0 and b[12 - end] > 0:
                score -= b[12 - end]

    return score


def alphabeta(b, depth, alpha, beta, is_maximizing):
    """
    Minimax with alpha-beta pruning.
    Maximizer = AI (side 1), Minimizer = player (side 0).
    Returns (score, best_pit).
    """
    terminal = sim_check_end(b)
    if terminal is not None:
        return (terminal[13] - terminal[6]) * 100, -1
    if depth == 0:
        return heuristic(b), -1

    if is_maximizing:
        side  = 1
        pits  = [i for i in range(7, 13) if b[i] > 0]
        if not pits:
            return heuristic(b), -1
        best_score, best_pit = float('-inf'), pits[0]
        for pit in pits:
            nb, free = sim_move(b, pit, side)
            next_max = free   # free turn → AI goes again → still maximizing
            score, _ = alphabeta(nb, depth - 1, alpha, beta, next_max)
            if score > best_score:
                best_score, best_pit = score, pit
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_pit
    else:
        side  = 0
        pits  = [i for i in range(6) if b[i] > 0]
        if not pits:
            return heuristic(b), -1
        best_score, best_pit = float('inf'), pits[0]
        for pit in pits:
            nb, free = sim_move(b, pit, side)
            next_max  = not free   # free turn = player goes again = still minimizing
            score, _  = alphabeta(nb, depth - 1, alpha, beta, next_max)
            if score < best_score:
                best_score, best_pit = score, pit
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_pit


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