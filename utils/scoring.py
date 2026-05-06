import json
from utils.database import (
    get_round, get_round_answers, get_all_players, save_score,
    get_round_scores, set_round_correct_answer
)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 1: "Ordena como puedas"
# Players rank 4 items. Scoring: 4 correct=10, 2 correct=5, 1 correct=-5, 0=0
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
            hits = sum(1 for i, v in enumerate(player_order) if i < len(correct) and v == correct[i])
            if hits == 4:
                base = 10
            elif hits >= 2:
                base = 5
            elif hits == 1:
                base = -5
            else:
                base = 0

        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id,base, final)

    return get_round_scores(round_id)


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 2: "Qué prefieres"
# Most-voted option = +10, least-voted = -10
# ═══════════════════════════════════════════════════════════════════════════════

def score_game2(round_id: int, game_id: int):

    answers = get_round_answers(round_id)

    # Count votes
    vote_count = {}
    for ans in answers:
        if ans["answer"]:
            vote_count[ans["answer"]] = vote_count.get(ans["answer"], 0) + 1

    if not vote_count:
        return []

    max_votes = max(vote_count.values())
    min_votes = min(vote_count.values())

    # If all options have same votes, everyone gets 0
    all_same = max_votes == min_votes

    for ans in answers:
        if ans["answer"] is None:
            base = 0
        elif all_same:
            base = 0
        elif vote_count.get(ans["answer"], 0) == max_votes:
            base = 10
        else:
            base = -10

        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id,base, final)

    # Store which option won as correct_answer
    winner = max(vote_count, key=vote_count.get)
    set_round_correct_answer(round_id, winner)

    return get_round_scores(round_id)


def get_game2_vote_summary(round_id: int):
    """Returns dict of {option: count}"""
    answers = get_round_answers(round_id)
    vote_count = {}
    for ans in answers:
        if ans["answer"]:
            vote_count[ans["answer"]] = vote_count.get(ans["answer"], 0) + 1
    return vote_count


# ═══════════════════════════════════════════════════════════════════════════════
# GAME 3: "Quién se acerca más"
# Numeric answer closest to real value wins. 
# Score = 10 - (20*(p-1)/(n-1))  where p=rank, n=num players
# ═══════════════════════════════════════════════════════════════════════════════

def score_game3(round_id: int):

    round_data = get_round(round_id)
    correct_value = float(round_data["correct_answer"])
    game_id = round_data["game_id"]

    answers = get_round_answers(round_id)

    # Parse numeric answers
    valid = []
    invalid_players = []
    
    for ans in answers:
        try:
            val = float(ans["answer"].replace(",", "."))
            valid.append({**ans, "numeric": val, "diff": abs(val - correct_value)})
        except (TypeError, ValueError, AttributeError):
            invalid_players.append(ans)

    # Sort by distance ascending (closest first)
    valid.sort(key=lambda x: x["diff"])

    n = len(valid)

    for i, ans in enumerate(valid):
        p = i + 1
        if n == 1:
            base = 10
        else:
            base = round(10 - (20 * (p - 1) / (n - 1)))

        double_bet = ans.get("double_bet", 0)
        final = base * 2 if double_bet else base
        save_score(ans["player_id"], round_id, game_id, base, final)


    for ans in invalid_players:
        double_bet = ans.get("double_bet", 0)
        save_score(ans["player_id"], round_id, game_id, 0)

    return get_round_scores(round_id)


def get_game3_ranked_answers(round_id: int, correct_value: float = None):
    """Return player answers sorted by proximity to correct value."""
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
