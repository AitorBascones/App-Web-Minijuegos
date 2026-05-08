import json
from utils.database import (
    get_round, get_round_answers, save_score,
    get_round_scores, set_round_correct_answer
)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 1: "Ordena como puedas"
# 4 hits=+10, 2 hits=+5, 1 hit=-5, 0 hits=0
# ═══════════════════════════════════════════════════════════════════════════════

def score_game1(round_id: int):
    round_data = get_round(round_id)
    correct = json.loads(round_data["correct_answer"])
    answers = get_round_answers(round_id)
    game_id = round_data["game_id"]

    for ans in answers:
        if ans["answer"] is None:
            base = 0
        else:
            player_order = json.loads(ans["answer"])
            hits = sum(
                1 for i, v in enumerate(player_order)
                if i < len(correct) and v == correct[i]
            )
            if hits == 4:
                base = 10
            elif hits >= 2:
                base = 5
            elif hits == 1:
                base = -5
            else:
                base = -10

        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id, final)

    return get_round_scores(round_id)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 2: "Qué prefieres"
# Mayoría gana +10, minoría -10; empate total = 0
# ═══════════════════════════════════════════════════════════════════════════════

def score_game2(round_id: int, game_id: int):
    answers = get_round_answers(round_id)

    vote_count = {}
    for ans in answers:
        if ans["answer"]:
            vote_count[ans["answer"]] = vote_count.get(ans["answer"], 0) + 1

    if not vote_count:
        return []

    max_votes = max(vote_count.values())
    num_options_with_max = sum(1 for v in vote_count.values() if v == max_votes)
    is_tie = num_options_with_max > 1

    for ans in answers:
        if ans["answer"] is None:
            base = 0
        elif is_tie and vote_count.get(ans["answer"], 0) == max_votes:
            base = 5
        elif not is_tie and vote_count.get(ans["answer"], 0) == max_votes:
            base = 10
        else:
            base = -10

        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id, final)

    winner = max(vote_count, key=vote_count.get)
    set_round_correct_answer(round_id, winner)

    return get_round_scores(round_id)


def get_game2_vote_summary(round_id: int):
    answers = get_round_answers(round_id)
    vote_count = {}
    for ans in answers:
        if ans["answer"]:
            vote_count[ans["answer"]] = vote_count.get(ans["answer"], 0) + 1
    return vote_count


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 3: "Quién se acerca más"
# Score = 10 - (20*(p-1)/(n-1)) donde p=rank, n=jugadores con respuesta válida
# ═══════════════════════════════════════════════════════════════════════════════

def score_game3(round_id: int):
    round_data = get_round(round_id)
    correct_value = float(round_data["correct_answer"])
    game_id = round_data["game_id"]
    answers = get_round_answers(round_id)

    valid = []
    invalid_players = []

    for ans in answers:
        try:
            val = float(ans["answer"].replace(",", "."))
            valid.append({**ans, "numeric": val, "diff": abs(val - correct_value)})
        except (TypeError, ValueError, AttributeError):
            invalid_players.append(ans)

    valid.sort(key=lambda x: x["diff"])
    n = len(valid)

    for i, ans in enumerate(valid):
        p = i + 1
        base = 10 if n == 1 else round(10 - (20 * (p - 1) / (n - 1)))
        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id, final)

    for ans in invalid_players:
        save_score(ans["player_id"], round_id, game_id, 0)

    return get_round_scores(round_id)


def get_game3_ranked_answers(round_id: int, correct_value: float = None):
    answers = get_round_answers(round_id)
    valid = []
    for ans in answers:
        try:
            val = float(ans["answer"].replace(",", "."))
            diff = abs(val - correct_value) if correct_value is not None else None
            valid.append({**ans, "numeric": val, "diff": diff})
        except (TypeError, ValueError, AttributeError):
            valid.append({**ans, "numeric": None, "diff": None})

    if correct_value is not None:
        valid.sort(key=lambda x: (x["diff"] is None, x["diff"] or 0))

    return valid
