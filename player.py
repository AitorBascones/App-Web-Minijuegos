"""
Player view — mobile-first interface for joining and playing.
Polls the DB to stay in sync with the admin's state machine.
"""
import json
import datetime
from collections import Counter
import streamlit as st
from utils.database import *
from utils.game_data import AVATARS, ROUND_DURATIONS
from utils.scoring import get_game2_vote_summary, get_game3_ranked_answers
import time

REACTION_EMOJIS = ["🎉", "🔥", "💀", "😂", "😤", "👀", "🤯", "💪"]

# Colores y etiquetas para las 4 opciones del juego de trivia
_G4_LABELS = ["🔷 A", "🔶 B", "🟢 C", "🔴 D"]
_G4_COLORS = ["#5b48e8", "#e8a813", "#1f9244", "#c93b3b"]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _score_color(score):
    if score > 0:
        return "#00c853"
    elif score < 0:
        return "#ff1744"
    return "#9e9e9e"


def _render_vote_bars(votes: dict, winner: str | None = None):
    """Barras horizontales de votos. winner resaltado en verde."""
    total = sum(votes.values()) or 1
    for opt, count in sorted(votes.items(), key=lambda x: -x[1]):
        pct = count / total
        is_winner = opt == winner
        bar_color = "#00c853" if is_winner else "#5b48e8"
        badge = " 🏆" if is_winner else ""
        st.markdown(
            f"<div style='margin:0.4rem 0;'>"
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='min-width:160px;font-size:0.9rem;'>{opt}{badge}</span>"
            f"<div style='background:{bar_color};height:22px;width:{pct*100:.0f}%;"
            f"border-radius:6px;min-width:4px;'></div>"
            f"<span style='font-size:0.85rem;opacity:0.8;'>{count} voto{'s' if count!=1 else ''}</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )


def _render_distance_bars(ranked: list, correct_value: float):
    """Barras de proximidad para Game 3. Más larga = más cercano."""
    valid = [r for r in ranked if r.get("diff") is not None]
    if not valid:
        return
    max_diff = max(r["diff"] for r in valid) or 1
    medals = ["🥇", "🥈", "🥉"]
    for i, ans in enumerate(ranked):
        diff = ans.get("diff")
        if diff is None:
            continue
        bar_pct = 1 - (diff / max_diff)
        # Gradient: 1st place green, last place red
        hue = int(120 * bar_pct)  # 120=green → 0=red
        bar_color = f"hsl({hue},80%,45%)"
        medal = medals[i] if i < 3 else f"{i+1}."
        diff_str = f"{diff:g}" if diff != int(diff) else str(int(diff))
        st.markdown(
            f"<div style='margin:0.35rem 0;'>"
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='min-width:24px;'>{medal}</span>"
            f"<span style='min-width:110px;font-size:0.85rem;'>{ans['avatar']} {ans['name']}</span>"
            f"<div style='background:{bar_color};height:20px;width:{bar_pct*100:.0f}%;"
            f"border-radius:6px;min-width:4px;'></div>"
            f"<span style='font-size:0.8rem;opacity:0.7;'>±{diff_str}</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )


def _render_countdown(started_at: str | None, game_id: int) -> int:
    """Muestra contador regresivo. Devuelve segundos restantes (999 si sin timer)."""
    if not started_at:
        return 999
    try:
        duration = ROUND_DURATIONS.get(game_id, 60)
        started = datetime.datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")
        elapsed = (datetime.datetime.utcnow() - started).total_seconds()
        remaining = max(0, duration - int(elapsed))
        pct = remaining / duration

        if pct > 0.5:
            color = "#00c853"
        elif pct > 0.25:
            color = "#ffab00"
        else:
            color = "#ff1744"

        label = f"⏱ {remaining}s" if remaining > 0 else "⏰ ¡Tiempo!"
        st.markdown(
            f"<div style='text-align:center;padding:0.2rem 0;'>"
            f"<span style='font-size:1.8rem;font-weight:900;color:{color};'>{label}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.progress(pct)
        return remaining
    except Exception:
        return 999


def _auto_submit_on_timeout(rnd: dict, game_id: int, player_id: int, answered_rounds: set):
    """Envía la respuesta actual (o un default) cuando se acaba el tiempo."""
    options = rnd["options"]
    round_id = rnd["round_id"]

    if game_id == 1:
        positions = {}
        for opt in options:
            positions[opt] = st.session_state.get(f"pos_{round_id}_{opt}", 1)
        sorted_items = sorted(enumerate(options), key=lambda x: positions[x[1]])
        answer = json.dumps([opt for _, opt in sorted_items])
    elif game_id == 2:
        answer = options[0] if options else "A"
    elif game_id == 3:
        raw = st.session_state.get(f"num_{round_id}", "")
        try:
            float(str(raw).replace(",", "."))
            answer = str(raw)
        except (ValueError, TypeError):
            answer = "1"
    elif game_id == 4:
        answer = options[0] if options else "A"
    else:
        answer = options[0] if options else "A"

    submit_answer(player_id, round_id, answer)
    answered_rounds.add(round_id)
    st.session_state["answered_rounds"] = answered_rounds


# ─────────────────────────────────────────────────────────────────────────────
# Entry
# ─────────────────────────────────────────────────────────────────────────────

def render_player():
    if "player_id" not in st.session_state:
        _render_join_screen()
        return

    player_id = st.session_state["player_id"]

    # Validate player still exists in DB (e.g. after a game reseed)
    if not get_player(player_id):
        st.session_state.clear()
        st.rerun()
        return

    player_name = st.session_state["player_name"]
    player_avatar = st.session_state["player_avatar"]

    st.markdown(
        f"<div style='text-align:right;color:rgba(255,255,255,0.6);font-size:0.85rem;'>"
        f"{player_avatar} {player_name}</div>",
        unsafe_allow_html=True,
    )

    current_game = get_current_game()

    # Admin ha compartido la clasificación: mostrarla en lugar del flujo normal
    if current_game and current_game.get("show_leaderboard"):
        _render_pushed_leaderboard(player_id)
        st.markdown("---")
        if st.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
        time.sleep(3)
        st.rerun()
        return

    if not current_game:
        all_games = get_all_games()
        if any(g["status"] == "finished" for g in all_games):
            _render_final_screen()
        else:
            _render_waiting_for_game()
        return

    game_id = current_game["game_id"]
    active_round = get_active_round_for_player(game_id)

    if not active_round:
        _render_waiting_for_round()
        return

    # Detect round/status transitions → purge stale widget state and force a clean render
    round_key = f"{active_round['round_id']}_{active_round['status']}"
    if st.session_state.get("_round_key") != round_key:
        st.session_state["_round_key"] = round_key
        for key in list(st.session_state.keys()):
            if key.startswith(("pos_", "num_")):
                del st.session_state[key]
        st.rerun()

    round_status = active_round["status"]

    if round_status == "announcing":
        _render_topic_announcement(active_round, current_game)
    elif round_status == "betting":
        _render_betting_phase(active_round, player_id)
    elif round_status == "active":
        _render_active_round(active_round, current_game, player_id)
    elif round_status == "results":
        _render_round_results(active_round, player_id)

    st.markdown("---")
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

    # Auto-refresh: 2s en espera/resultados, 1s en active (para que el countdown avance)
    if round_status in ("announcing", "betting", "results"):
        time.sleep(2)
        st.rerun()
    elif round_status == "active":
        answered_rounds = st.session_state.get("answered_rounds", set())
        already_answered = active_round["round_id"] in answered_rounds
        if not already_answered:
            existing = get_player_choice(player_id, active_round["round_id"])
            already_answered = bool(existing and existing.get("answer"))
        # 1s si aún no respondió (countdown visible) · 2s si espera resultados
        time.sleep(1 if not already_answered else 2)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Join screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_join_screen():
    st.markdown("<h1 style='text-align:center;'>🎮 Las Vascongadas</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:rgba(255,255,255,0.45);font-size:0.85rem;margin-top:-0.8rem;'>"
        "Una producción del Señor Vascones 👑</p>",
        unsafe_allow_html=True,
    )

    players = get_all_players()
    if players:
        st.markdown(
            f"<div style='text-align:center;color:rgba(255,255,255,0.6);font-size:0.9rem;margin-bottom:1rem;'>"
            f"👥 {len(players)} jugador{'es' if len(players) != 1 else ''} ya en sala</div>",
            unsafe_allow_html=True,
        )

    with st.form("join_form"):
        name = st.text_input("Tu nombre", placeholder="Ej: Débora Melo", max_chars=24)
        avatar = st.selectbox("Elige tu Avatar", AVATARS, index=0)

        if st.form_submit_button("🚀 ¡Unirme!", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Introduce tu nombre")
                return
            # Reconnect with saved player_id if name matches an existing player
            all_players = get_all_players()
            existing = next((p for p in all_players if p["name"].lower() == name.strip().lower()), None)
            if existing:
                player_id = existing["player_id"]
                player_avatar = existing["avatar"]
            else:
                player_id = add_player(name.strip(), avatar)
                player_avatar = avatar
            st.session_state.update({
                "player_id": player_id,
                "player_name": name.strip(),
                "player_avatar": player_avatar,
                "answered_rounds": set(),
                "bet_rounds": set(),
            })
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Lobby / waiting screens
# ─────────────────────────────────────────────────────────────────────────────

def _render_waiting_for_game():
    players = get_all_players()
    st.markdown(
        "<div class='topic-banner'>"
        "<h2>⏳ Esperando a que el administrador seleccione un juego...</h2>"
        "<p>El Señor Vascones está preparando algo épico...</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    if players:
        st.markdown(
            f"<div class='notif-box'>👥 {len(players)} jugador{'es' if len(players)!=1 else ''} "
            f"conectado{'s' if len(players)!=1 else ''} en sala</div>",
            unsafe_allow_html=True,
        )
    time.sleep(3)
    st.rerun()


def _render_waiting_for_round():
    st.markdown(
        "<div class='topic-banner'>"
        "<h2>⏳ Esperando la siguiente ronda...</h2>"
        "<p>El Señor Vascones está consultando sus fuentes secretas...</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    time.sleep(3)
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Topic announcement
# ─────────────────────────────────────────────────────────────────────────────

def _render_topic_announcement(rnd, game):
    st.markdown(
        f"<div class='topic-banner'>"
        f"<p style='opacity:0.7;font-size:0.9rem;text-transform:uppercase;letter-spacing:2px;'>{game['title']}</p>"
        f"<h1 style='margin:0.5rem 0;font-size:2.5rem;'>{rnd['topic']}</h1>"
        f"<p style='opacity:0.8;'>Ronda {rnd['round_number']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='notif-box'>📢 ¡Prepárate! El administrador abrirá la fase de apuesta pronto.</div>",
        unsafe_allow_html=True,
    )
    st.caption("💡 Dato del Señor Vascones: confía en tus instintos (o no, él tampoco lo sabe)")


# ─────────────────────────────────────────────────────────────────────────────
# Betting phase
# ─────────────────────────────────────────────────────────────────────────────

def _render_betting_phase(rnd, player_id):
    bet_rounds = st.session_state.get("bet_rounds", set())

    st.markdown(
        f"<div class='topic-banner'>"
        f"<h2>💰 Fase de apuesta</h2>"
        f"<h3>{rnd['topic']}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    already_bet = rnd["round_id"] in bet_rounds
    if not already_bet:
        existing = get_player_choice(player_id, rnd["round_id"])
        already_bet = existing is not None

    if already_bet:
        existing = get_player_choice(player_id, rnd["round_id"])
        is_double = bool(existing and existing.get("double_bet"))
        bet_count = count_bets_submitted(rnd["round_id"])
        total = len(get_all_players())
        st.markdown(
            f"<div class='notif-box'>✅ ¡Apuesta registrada! "
            f"<b>{bet_count}/{total}</b> han apostado.</div>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        for col, this_double, icon, label in [
            (col1, True,  "🔥", "¡Apuesta doble! ×2"),
            (col2, False, "😐", "Puntuación normal"),
        ]:
            chosen = is_double == this_double
            bg      = "#5b48e8" if chosen else "rgba(255,255,255,0.05)"
            opacity = "0.9"     if chosen else "0.25"
            check   = "✅ "     if chosen else ""
            with col:
                st.markdown(
                    f"<div style='background:{bg};border-radius:10px;padding:0.7rem;"
                    f"text-align:center;opacity:{opacity};margin-bottom:0.3rem;'>"
                    f"<span style='color:white;font-weight:700;'>{check}{icon} {label}</span></div>",
                    unsafe_allow_html=True,
                )
        return

    st.markdown(
        "<h3 style='text-align:center;'>¿Quieres multiplicar tu puntuación ×2?</h3>"
        "<p style='text-align:center;color:rgba(255,255,255,0.7);'>"
        "Si apuestas doble, tu puntuación (positiva O negativa) se multiplicará por 2.</p>",
        unsafe_allow_html=True,
    )
    st.caption("⚠️ El Señor Vascones no se hace responsable de las decisiones tomadas bajo presión.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 ¡Apuesta doble! ×2", use_container_width=True, type="primary"):
            submit_double_bet(player_id, rnd["round_id"], True)
            bet_rounds.add(rnd["round_id"])
            st.session_state["bet_rounds"] = bet_rounds
            st.rerun()
    with col2:
        if st.button("😐 Puntuación normal", use_container_width=True):
            submit_double_bet(player_id, rnd["round_id"], False)
            bet_rounds.add(rnd["round_id"])
            st.session_state["bet_rounds"] = bet_rounds
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Active round (answer phase)
# ─────────────────────────────────────────────────────────────────────────────

def _render_active_round(rnd, game, player_id):
    answered_rounds = st.session_state.get("answered_rounds", set())
    existing = get_player_choice(player_id, rnd["round_id"])
    game_type = game["game_id"]

    if rnd["round_id"] in answered_rounds or (existing and existing.get("answer")):
        _render_already_answered(rnd, player_id, game_type)
        return

    # Countdown — solo visible cuando el jugador aún no ha respondido
    remaining = _render_countdown(rnd.get("started_at"), game_type)

    st.markdown(
        f"<div class='topic-banner' style='padding:1rem;'>"
        f"<p style='opacity:0.7;font-size:0.85rem;'>{rnd['topic']}</p>"
        f"<h2 style='margin:0;'>{rnd['question']}</h2>"
        f"</div>",
        unsafe_allow_html=True,
    )

    bet_choice = existing.get("double_bet", 0) if existing else 0
    if bet_choice:
        st.markdown(
            "<div style='text-align:center;color:#FFD700;font-weight:800;margin:0.5rem 0;'>🔥 Apuesta doble activa</div>",
            unsafe_allow_html=True,
        )

    if game_type == 1:
        _render_game1_answer(rnd, player_id, answered_rounds)
    elif game_type == 2:
        _render_game2_answer(rnd, player_id, answered_rounds)
    elif game_type == 3:
        _render_game3_answer(rnd, player_id, answered_rounds)
    elif game_type == 4:
        _render_game4_answer(rnd, player_id, answered_rounds)

    # Auto-submit cuando el tiempo se agota (se evalúa tras renderizar widgets)
    if remaining == 0:
        answered_rounds = st.session_state.get("answered_rounds", set())
        if rnd["round_id"] not in answered_rounds:
            _auto_submit_on_timeout(rnd, game_type, player_id, answered_rounds)
        st.rerun()


def _render_already_answered(rnd, player_id, game_id):
    """Muestra la respuesta enviada en estado bloqueado y difuminado. Sin animaciones."""
    existing = get_player_choice(player_id, rnd["round_id"])
    my_answer = existing.get("answer") if existing else None
    answered_count = count_answers_submitted(rnd["round_id"])
    total = len(get_all_players())

    st.markdown(
        f"<div class='notif-box'>✅ ¡Respuesta enviada! "
        f"<b>{answered_count}/{total}</b> han respondido.</div>",
        unsafe_allow_html=True,
    )
    st.caption("🕐 El Señor Vascones cronometra cada segundo de tu sufrimiento.")

    st.markdown(
        f"<div style='opacity:0.4;padding:0.4rem 0 0.8rem;'>"
        f"<p style='font-size:0.8rem;margin:0;'>{rnd['topic']}</p>"
        f"<h3 style='margin:0.2rem 0;'>{rnd['question']}</h3>"
        f"</div>",
        unsafe_allow_html=True,
    )

    options = rnd.get("options", [])

    if game_id in (2, 4):
        for i, opt in enumerate(options):
            is_chosen = opt == my_answer
            if is_chosen:
                bg = _G4_COLORS[i] if game_id == 4 and i < len(_G4_COLORS) else "#5b48e8"
                prefix = f"{_G4_LABELS[i]} " if game_id == 4 and i < len(_G4_LABELS) else "👉 "
                st.markdown(
                    f"<div style='background:{bg};border-radius:10px;padding:0.7rem 1rem;"
                    f"margin:0.3rem 0;opacity:0.9;'>"
                    f"<span style='color:white;font-weight:700;'>✅ {prefix}{opt}</span></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.04);"
                    f"border:1px solid rgba(255,255,255,0.08);border-radius:10px;"
                    f"padding:0.7rem 1rem;margin:0.3rem 0;opacity:0.25;'>{opt}</div>",
                    unsafe_allow_html=True,
                )

    elif game_id == 1 and my_answer:
        try:
            ordered = json.loads(my_answer)
            for i, item in enumerate(ordered, 1):
                st.markdown(
                    f"<div style='padding:0.4rem 0.8rem;margin:0.2rem 0;opacity:0.45;"
                    f"background:rgba(255,255,255,0.06);border-radius:8px;'>{i}. {item}</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    elif game_id == 3 and my_answer:
        st.markdown(
            f"<div style='text-align:center;font-size:1.5rem;font-weight:700;opacity:0.5;"
            f"padding:0.5rem;'>Tu respuesta: {my_answer}</div>",
            unsafe_allow_html=True,
        )


def _render_waiting_for_results(rnd):
    answered_count = count_answers_submitted(rnd["round_id"])
    total = len(get_all_players())
    st.markdown(
        f"<div class='notif-box'>"
        f"✅ ¡Respuesta enviada! Esperando a los demás...<br>"
        f"<b>{answered_count}/{total}</b> jugadores han respondido.</div>",
        unsafe_allow_html=True,
    )


# ── Game 1: Order ──────────────────────────────────────────────────────────────

def _render_game1_answer(rnd, player_id, answered_rounds):
    options = rnd["options"]
    st.markdown("### 🔢 Establece el orden (1 = primero)")
    st.caption("Asigna una posición diferente a cada elemento")

    with st.form(f"game1_form_{rnd['round_id']}"):
        positions = {}
        for opt in options:
            pos = st.selectbox(
                f"**{opt}**",
                options=[1, 2, 3, 4],
                key=f"pos_{rnd['round_id']}_{opt}",
            )
            positions[opt] = pos

        submitted = st.form_submit_button("✅ Confirmar orden", type="primary", use_container_width=True)
        if submitted:
            dupes = [str(p) for p, c in Counter(positions.values()).items() if c > 1]
            if dupes:
                st.error(f"⚠️ La posición {', '.join(dupes)} está asignada a más de un elemento")
            else:
                ordered = sorted(positions.keys(), key=lambda x: positions[x])
                submit_answer(player_id, rnd["round_id"], json.dumps(ordered))
                answered_rounds.add(rnd["round_id"])
                st.session_state["answered_rounds"] = answered_rounds
                st.rerun()

    st.caption("💡 Si hay empate en posiciones, el sistema tomará el orden de arriba a abajo.")


# ── Game 2: Preference ─────────────────────────────────────────────────────────

def _render_game2_answer(rnd, player_id, answered_rounds):
    options = rnd["options"]
    st.markdown("### 🤔 ¿Qué prefieres?")
    st.caption("Elige la opción que crees que votará la mayoría para ganar puntos.")

    for opt in options:
        if st.button(f"👉 {opt}", key=f"pref_{rnd['round_id']}_{opt}", use_container_width=True):
            submit_answer(player_id, rnd["round_id"], opt)
            answered_rounds.add(rnd["round_id"])
            st.session_state["answered_rounds"] = answered_rounds
            st.success(f"✅ Has votado: **{opt}**")
            st.rerun()


# ── Game 3: Numeric ────────────────────────────────────────────────────────────

def _render_game3_answer(rnd, player_id, answered_rounds):
    st.markdown("### 🎯 ¿Cuánto crees que es?")
    st.caption("Escribe un número. ¡El más cercano gana más puntos!")

    with st.form(f"game3_form_{rnd['round_id']}"):
        answer = st.text_input(
            "Tu respuesta numérica",
            placeholder="Ej: 69",
            key=f"num_{rnd['round_id']}",
        )
        submitted = st.form_submit_button("✅ Enviar respuesta", type="primary", use_container_width=True)
        if submitted:
            if not answer.strip():
                st.error("Introduce un número.")
            else:
                try:
                    float(answer.replace(",", "."))
                    submit_answer(player_id, rnd["round_id"], answer.strip())
                    answered_rounds.add(rnd["round_id"])
                    st.session_state["answered_rounds"] = answered_rounds
                    st.success("✅ ¡Respuesta enviada!")
                    st.rerun()
                except ValueError:
                    st.error("Por favor introduce solo números (puedes usar coma o punto decimal).")


# ── Game 4: Trivia ─────────────────────────────────────────────────────────────

def _render_game4_answer(rnd, player_id, answered_rounds):
    options = rnd["options"]
    st.markdown("### 🧠 ¿Cuál es la respuesta correcta?")
    st.caption("Solo hay una respuesta correcta. ¡Decide rápido!")

    col1, col2 = st.columns(2)
    cols = [col1, col2, col1, col2]

    for i, opt in enumerate(options[:4]):
        label = _G4_LABELS[i]
        color = _G4_COLORS[i]
        with cols[i]:
            st.markdown(
                f"<div style='background:{color};border-radius:10px;padding:0.6rem 0.4rem;"
                f"text-align:center;margin-bottom:0.3rem;'>"
                f"<span style='color:white;font-size:0.75rem;font-weight:700;'>{label}</span><br>"
                f"<span style='color:white;font-size:0.9rem;'>{opt}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button(
                "Elegir",
                key=f"g4_{rnd['round_id']}_{i}",
                use_container_width=True,
            ):
                submit_answer(player_id, rnd["round_id"], opt)
                answered_rounds.add(rnd["round_id"])
                st.session_state["answered_rounds"] = answered_rounds
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Results screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_round_results(rnd, player_id):
    # If a newer round has already opened for betting/active, hide old scores
    all_rounds = get_all_rounds(rnd["game_id"])
    if any(
        r["round_number"] > rnd["round_number"] and r["status"] in ("betting", "active")
        for r in all_rounds
    ):
        st.markdown(
            "<div class='topic-banner'>"
            "<h2>⏳ ¡Siguiente ronda en marcha!</h2>"
            "<p>Actualiza para ver las apuestas.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    scores = get_round_scores(rnd["round_id"])
    game_id = rnd["game_id"]

    st.markdown(f"## 📊 Resultados — {rnd['topic']}")

    # ── Reveal según tipo de juego ──────────────────────────────────────────
    if game_id == 1 and rnd.get("correct_answer"):
        try:
            correct_list = json.loads(rnd["correct_answer"])
            st.markdown(
                f"<div style='background:rgba(0,200,83,0.15);border:2px solid #00c853;"
                f"border-radius:14px;padding:1rem;color:white;margin:0.5rem 0;'>"
                f"✅ <b>Orden correcto:</b> {' → '.join(correct_list)}</div>",
                unsafe_allow_html=True,
            )
        except Exception:
            pass

    elif game_id == 2:
        votes = get_game2_vote_summary(rnd["round_id"])
        if votes:
            st.markdown("**Distribución de votos:**")
            _render_vote_bars(votes, winner=rnd.get("correct_answer"))

    elif game_id == 3 and rnd.get("correct_answer"):
        try:
            correct_val = float(rnd["correct_answer"])
            st.markdown(
                f"<div style='background:rgba(0,200,83,0.15);border:2px solid #00c853;"
                f"border-radius:14px;padding:1rem;color:white;text-align:center;margin:0.5rem 0;'>"
                f"🎯 <b>Respuesta correcta: {correct_val:g}</b></div>",
                unsafe_allow_html=True,
            )
            ranked = get_game3_ranked_answers(rnd["round_id"], correct_val)
            if ranked:
                st.markdown("**Proximidad al valor correcto:**")
                _render_distance_bars(ranked, correct_val)
        except Exception:
            pass

    elif game_id == 4 and rnd.get("correct_answer"):
        correct = rnd["correct_answer"]
        st.markdown(
            f"<div style='background:rgba(0,200,83,0.15);border:2px solid #00c853;"
            f"border-radius:14px;padding:1rem;color:white;text-align:center;margin:0.5rem 0;'>"
            f"✅ <b>Respuesta correcta: {correct}</b></div>",
            unsafe_allow_html=True,
        )
        votes = get_game2_vote_summary(rnd["round_id"])
        if votes:
            st.markdown("**Distribución de votos:**")
            _render_vote_bars(votes, winner=correct)

        # Indicador personal
        my_choice = get_player_choice(player_id, rnd["round_id"])
        if my_choice and my_choice.get("answer"):
            if my_choice["answer"] == correct:
                st.markdown(
                    "<div class='notif-box'>✅ ¡Acertaste! Tu respuesta fue correcta.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='notif-box' style='border-color:#ff1744;'>"
                    f"❌ Respondiste: <b>{my_choice['answer']}</b></div>",
                    unsafe_allow_html=True,
                )

    # ── Puntuaciones de la ronda ────────────────────────────────────────────
    st.markdown("---")
    st.caption("📜 El Señor Vascones ha revisado los resultados. Dice que no se esperaba esto de vosotros.")
    st.markdown("### 🏆 Puntuación de la ronda")

    # Para Game 4: badge ⚡ al más rápido entre los que acertaron
    fastest_pid = None
    if game_id == 4:
        correct_with_time = [
            (s["answered_at"], s["player_id"])
            for s in scores
            if s.get("answered_at") and s["final_score"] > 0
        ]
        if correct_with_time:
            fastest_pid = min(correct_with_time, key=lambda x: x[0])[1]

    medals = ["🥇", "🥈", "🥉"]
    for i, s in enumerate(scores):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = s["player_id"] == player_id
        score = s["final_score"]
        color = _score_color(score)
        sign = "+" if score > 0 else ""
        double_str = " 🔥×2" if s["double_bet"] else ""
        speed_str = " ⚡" if s["player_id"] == fastest_pid else ""
        highlight = "border: 2px solid #FFD700;" if is_me else ""

        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{s["avatar"]} {s["name"]}'
            f'{" (tú)" if is_me else ""}{speed_str}</span>'
            f'<span style="color:{color};font-weight:800;font-size:1.1rem;">'
            f'{sign}{score} pts{double_str}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Clasificación general ───────────────────────────────────────────────
    st.markdown("---")
    lb = get_leaderboard()
    st.markdown("### 📋 Clasificación general")
    for i, row in enumerate(lb):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = row["player_id"] == player_id
        highlight = "border: 2px solid #FFD700;" if is_me else ""
        score = row["total_score"]
        sign = "+" if score > 0 else ""
        color = _score_color(score)
        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{row["avatar"]} {row["name"]}'
            f'{" (tú)" if is_me else ""}</span>'
            f'<span style="color:{color};font-weight:800;">{sign}{score} pts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Reacciones ──────────────────────────────────────────────────────────
    _render_reactions(rnd["round_id"], player_id)


# ─────────────────────────────────────────────────────────────────────────────
# Reactions
# ─────────────────────────────────────────────────────────────────────────────

def _render_reactions(round_id: int, player_id: int):
    st.markdown("---")
    reactions = get_reactions(round_id)

    if reactions:
        parts = "  ".join(f"{emoji} **{cnt}**" for emoji, cnt in reactions.items())
        st.markdown(
            f"<div style='text-align:center;font-size:1.3rem;padding:0.4rem;'>{parts}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<p style='text-align:center;opacity:0.6;font-size:0.85rem;'>¡Reacciona!</p>",
                unsafe_allow_html=True)
    cols = st.columns(len(REACTION_EMOJIS))
    for i, emoji in enumerate(REACTION_EMOJIS):
        with cols[i]:
            if st.button(emoji, key=f"react_{round_id}_{emoji}_{player_id}"):
                submit_reaction(player_id, round_id, emoji)
                st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Final screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_pushed_leaderboard(player_id: int):
    lb = get_leaderboard()
    n = len(lb)
    my_pos = next((i for i, r in enumerate(lb) if r["player_id"] == player_id), -1)

    st.markdown("""<style>
@keyframes zoomIn {
    from { transform: scale(0.6); opacity: 0; }
    to   { transform: scale(1);   opacity: 1; }
}
@keyframes slideUp {
    from { transform: translateY(30px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}
.lb-hero   { animation: zoomIn  0.7s cubic-bezier(0.22,1,0.36,1) both; }
.lb-detail { animation: slideUp 0.5s ease 0.6s both; }
.lb-table  { animation: slideUp 0.5s ease 0.9s both; }
</style>""", unsafe_allow_html=True)

    # Position-specific style
    if my_pos == 0:
        pos_label, pos_color = "🥇 ¡PRIMERO!", "#FFD700"
        bg = "rgba(255,215,0,0.15)"; border = "#FFD700"
    elif my_pos == 1:
        pos_label, pos_color = "🥈 Segundo", "#C0C0C0"
        bg = "rgba(192,192,192,0.12)"; border = "#C0C0C0"
    elif my_pos == 2:
        pos_label, pos_color = "🥉 Tercero", "#CD7F32"
        bg = "rgba(205,127,50,0.12)"; border = "#CD7F32"
    elif my_pos >= 0:
        pos_label, pos_color = f"#{my_pos + 1}", "#5b48e8"
        bg = "rgba(91,72,232,0.12)"; border = "#5b48e8"
    else:
        pos_label, pos_color = "?", "#9e9e9e"
        bg = "rgba(158,158,158,0.08)"; border = "#9e9e9e"

    my_score = lb[my_pos]["total_score"] if my_pos >= 0 else 0
    my_avatar = lb[my_pos]["avatar"] if my_pos >= 0 else ""
    my_name  = lb[my_pos]["name"]   if my_pos >= 0 else ""

    st.markdown(
        f"<div class='lb-hero' style='background:{bg};border:3px solid {border};"
        f"border-radius:20px;padding:2rem 1.5rem;text-align:center;margin:0.5rem 0;'>"
        f"<div style='font-size:0.8rem;opacity:0.6;letter-spacing:3px;"
        f"text-transform:uppercase;margin-bottom:0.3rem;'>📊 Clasificación</div>"
        f"<div style='font-size:4.5rem;font-weight:900;color:{pos_color};"
        f"line-height:1;margin:0.4rem 0;'>{pos_label}</div>"
        f"<div style='font-size:1.4rem;margin:0.2rem 0;'>{my_avatar} {my_name}</div>"
        f"<div style='font-size:2rem;font-weight:800;color:{pos_color};'>"
        f"{'+' if my_score > 0 else ''}{my_score} pts</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Above / below contextual info
    above = lb[my_pos - 1] if my_pos > 0 else None
    below = lb[my_pos + 1] if 0 <= my_pos < n - 1 else None

    if above:
        diff = above["total_score"] - my_score
        st.markdown(
            f"<div class='lb-detail' style='background:rgba(255,255,255,0.06);"
            f"border-radius:10px;padding:0.6rem 1rem;margin:0.3rem 0;font-size:0.95rem;'>"
            f"⬆️ {above['avatar']} <b>{above['name']}</b> está <b>{diff} pts</b> por encima"
            f"</div>",
            unsafe_allow_html=True,
        )
    if below and my_pos == 0:
        diff = my_score - below["total_score"]
        st.markdown(
            f"<div class='lb-detail' style='background:rgba(255,215,0,0.1);"
            f"border-radius:10px;padding:0.6rem 1rem;margin:0.3rem 0;font-size:0.95rem;"
            f"color:#FFD700;font-weight:700;'>"
            f"🏆 Llevas <b>{diff} pts</b> de ventaja sobre {below['avatar']} {below['name']}"
            f"</div>",
            unsafe_allow_html=True,
        )
    elif below:
        diff = my_score - below["total_score"]
        st.markdown(
            f"<div class='lb-detail' style='background:rgba(255,255,255,0.06);"
            f"border-radius:10px;padding:0.6rem 1rem;margin:0.3rem 0;font-size:0.95rem;'>"
            f"⬇️ {below['avatar']} <b>{below['name']}</b> está <b>{diff} pts</b> por debajo"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Full table
    st.markdown("---")
    medals = ["🥇", "🥈", "🥉"]
    st.markdown("<div class='lb-table'>", unsafe_allow_html=True)
    for i, row in enumerate(lb):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = row["player_id"] == player_id
        highlight = "border: 2px solid #FFD700;" if is_me else ""
        score = row["total_score"]
        sign = "+" if score > 0 else ""
        color = _score_color(score)
        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{row["avatar"]} {row["name"]}'
            f'{" (tú)" if is_me else ""}</span>'
            f'<span style="color:{color};font-weight:800;">{sign}{score} pts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_final_screen():
    st.markdown(
        "<div class='topic-banner'>"
        "<h1>🏆 ¡Juego finalizado!</h1>"
        "<p>Gracias por participar. ¡Aquí están los resultados finales!</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    lb = get_leaderboard()
    player_id = st.session_state.get("player_id")
    medals = ["🥇", "🥈", "🥉"]

    st.markdown("### 🏆 Clasificación Final")
    for i, row in enumerate(lb):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = row["player_id"] == player_id
        highlight = "border: 2px solid #FFD700;" if is_me else ""
        score = row["total_score"]
        sign = "+" if score > 0 else ""
        color = _score_color(score)
        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{row["avatar"]} {row["name"]}'
            f'{" (tú)" if is_me else ""}</span>'
            f'<span style="color:{color};font-weight:800;font-size:1.1rem;">{sign}{score} pts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        "<p style='text-align:center;color:rgba(255,255,255,0.4);font-size:0.85rem;margin-top:1.5rem;'>"
        "Las Vascongadas • Juego diseñado por el <b>Señor Vascones</b></p>",
        unsafe_allow_html=True,
    )
