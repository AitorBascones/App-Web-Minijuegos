"""
Player view — mobile-first interface for joining and playing.
Polls the DB to stay in sync with the admin's state machine.
"""
import json
import streamlit as st
from utils.database import *
from utils.game_data import AVATARS
from utils.scoring import get_game2_vote_summary, get_game3_ranked_answers
import time

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _score_color(score):
    if score > 0:
        return "#00c853"
    elif score < 0:
        return "#ff1744"
    return "#9e9e9e"


# ─────────────────────────────────────────────────────────────────────────────
# Entry
# ─────────────────────────────────────────────────────────────────────────────

def render_player():
     # 1. Registro / Login persistente
    if "player_id" not in st.session_state:
        _render_join_screen()
        return

    player_id = st.session_state["player_id"]
    player_name = st.session_state["player_name"]
    player_avatar = st.session_state["player_avatar"]

    # Header simple
    st.markdown(
        f"<div style='text-align:right;color:rgba(255,255,255,0.6);font-size:0.85rem;'>"
        f"{player_avatar} {player_name}</div>",
        unsafe_allow_html=True,
    )
    
    current_game=get_current_game()
    
    if not current_game:
        _render_waiting_for_game()
        return
    
    game_id=current_game["game_id"]
    
  # 2. Obtener datos de la ultima ronda activa
    active_round = get_active_round_for_game(game_id)

    if not active_round:
        _render_waiting_for_round()
        return


    # Game_id y status de la ronda activa
    round_status = active_round["status"]

    #Dependiendo del estado de la ronda carga una pantalla u otra
    if round_status == "announcing":
        _render_topic_announcement(active_round, current_game)
    elif round_status == "betting":
        _render_betting_phase(active_round, player_id)
    elif round_status == "active":
        _render_active_round(active_round, current_game, player_id)
    elif round_status == "results":
        _render_round_results(active_round, player_id)

    # Botón de actualización manual
    st.markdown("---")
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

    # Auto-refresh en fases de espera
    if round_status in ("announcing", "betting"):
        time.sleep(3)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Join screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_join_screen():
    st.markdown("<h1 style='text-align:center;'>🎮 MiniGames</h1>", unsafe_allow_html=True)
    
    with st.form("join_form"):
        name = st.text_input("Tu nombre", placeholder="Ej: Débora Melo ", max_chars=24)
        avatar = st.selectbox("Elige tu Avatar", AVATARS, index=0)
        
        if st.form_submit_button("🚀 ¡Unirme!", type="primary", use_container_width=True):
            if not name.strip():
                st.error("Introduce tu nombre")
                return
            
           
            player_id = add_player(name.strip(), avatar)
            st.session_state.update({
                "player_id": player_id,
                "player_name": name.strip(),
                "player_avatar": avatar
            })
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Lobby
# ─────────────────────────────────────────────────────────────────────────────

def _render_waiting_for_game():
    st.markdown(
        "<div class='topic-banner'>"
        "<h2>⏳ Esperando a que el administrador seleccione un juego...</h2>"
        "<p>Permanece atento.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    time.sleep(3)
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Waiting for round
# ─────────────────────────────────────────────────────────────────────────────

def _render_waiting_for_round():
    st.markdown(
        "<div class='topic-banner'>"
        "<h2>⏳ Esperando la siguiente ronda...</h2>"
        "<p>El administrador iniciará pronto.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    import time
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

    if rnd["round_id"] in bet_rounds:
        existing = get_player_choice(player_id, rnd["round_id"])
        bet_str = "🔥 ¡APUESTA DOBLE!" if existing and existing["double_bet"] else "👍 Puntuación normal"
        st.markdown(
            f"<div class='notif-box'>✅ Has elegido: {bet_str}<br>Esperando que empiece la ronda...</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        "<h3 style='text-align:center;'>¿Quieres multiplicar tu puntuación ×2?</h3>"
        "<p style='text-align:center;color:rgba(255,255,255,0.7);'>"
        "Si apuestas doble, tu puntuación (positiva O negativa) se multiplicará por 2.</p>",
        unsafe_allow_html=True,
    )

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

    # Check if already answered
    existing = get_player_choice(player_id, rnd["round_id"])
    if rnd["round_id"] in answered_rounds or (existing and existing.get("answer")):
        _render_waiting_for_results(rnd)
        return

    st.markdown(
        f"<div class='topic-banner' style='padding:1rem;'>"
        f"<p style='opacity:0.7;font-size:0.85rem;'>{rnd['topic']}</p>"
        f"<h2 style='margin:0;'>{rnd['question']}</h2>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Show double bet status
    bet_choice = existing.get("double_bet", 0) if existing else 0
    if bet_choice:
        st.markdown(
            "<div style='text-align:center;color:#FFD700;font-weight:800;margin:0.5rem 0;'>🔥 Apuesta doble activa</div>",
            unsafe_allow_html=True,
        )

    game_type = game["game_id"]

    if game_type == 1:
        _render_game1_answer(rnd, player_id, answered_rounds)
    elif game_type == 2:
        _render_game2_answer(rnd, player_id, answered_rounds)
    elif game_type == 3:
        _render_game3_answer(rnd, player_id, answered_rounds)


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
            # Build ordered list by assigned position
            ordered = sorted(positions.keys(), key=lambda x: positions[x])
            answer = json.dumps(ordered)
            submit_answer(player_id, rnd["round_id"], answer)
            answered_rounds.add(rnd["round_id"])
            st.session_state["answered_rounds"] = answered_rounds
            st.success("✅ ¡Respuesta enviada!")
            st.rerun()

    # Visual helper
    st.markdown("---")
    st.caption("💡 Si hay empate en posiciones, el sistema tomará el orden de arriba a abajo.")


# ── Game 2: Preference ─────────────────────────────────────────────────────────

def _render_game2_answer(rnd, player_id, answered_rounds):
    options = rnd["options"]

    st.markdown("### 🤔 ¿Qué prefieres?")
    st.caption("Elige la opción que crees que votará la mayoría para ganar puntos.")

    for opt in options:
        if st.button(
            f"👉 {opt}",
            key=f"pref_{rnd['round_id']}_{opt}",
            use_container_width=True,
        ):
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


# ─────────────────────────────────────────────────────────────────────────────
# Results screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_round_results(rnd, player_id, edition_id):
    scores = get_round_scores(rnd["round_id"])
    game_id = rnd["game_id"]

    st.markdown(f"## 📊 Resultados — {rnd['topic']}")

    # Correct answer info
    if rnd.get("correct_answer"):
        
        if game_id == 1:
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
            st.markdown("**Distribución de votos:**")
            for opt, count in sorted(votes.items(), key=lambda x: -x[1]):
                winner_mark = " 🏆" if opt == rnd["correct_answer"] else ""
                st.markdown(f"- {opt}: **{count}** votos{winner_mark}")
        
        elif game_id == 3:
            try:
                correct_val = float(rnd["correct_answer"])
                st.markdown(
                    f"<div style='background:rgba(0,200,83,0.15);border:2px solid #00c853;"
                    f"border-radius:14px;padding:1rem;color:white;text-align:center;margin:0.5rem 0;'>"
                    f"🎯 <b>Respuesta correcta: {correct_val:g}</b></div>",
                    unsafe_allow_html=True,
                )
                ranked = get_game3_ranked_answers(rnd["round_id"], correct_val)
                st.markdown("**Ranking de respuestas:**")
                for i, ans in enumerate(ranked):
                    diff_str = f"(diferencia: {ans['diff']:g})" if ans["diff"] is not None else ""
                    me_str = " ← tú" if ans["player_id"] == player_id else ""
                    st.markdown(f"{i+1}. {ans['avatar']} **{ans['name']}**: {ans['answer']} {diff_str}{me_str}")
            except Exception:
                pass

    st.markdown("---")
    st.markdown("### 🏆 Puntuación de la ronda")

    medals = ["🥇", "🥈", "🥉"]
    for i, s in enumerate(scores):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = s["player_id"] == player_id
        score = s["final_score"]
        color = _score_color(score)
        sign = "+" if score > 0 else ""
        double_str = " 🔥×2" if s["double_bet"] else ""
        highlight = "border: 2px solid #FFD700;" if is_me else ""

        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{s["avatar"]} {s["name"]}{" (tú)" if is_me else ""}</span>'
            f'<span style="color:{color};font-weight:800;font-size:1.1rem;">{sign}{score} pts{double_str}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    
    # Overall leaderboard
    lb = get_leaderboard(edition_id)
    st.markdown("### 📋 Clasificación general")
    for i, row in enumerate(lb):
        medal = medals[i] if i < 3 else f"{i+1}."
        is_me = row["id"] == player_id
        highlight = "border: 2px solid #FFD700;" if is_me else ""
        score = row["total_score"]
        sign = "+" if score > 0 else ""
        color = _score_color(score)
        st.markdown(
            f'<div class="lb-row" style="{highlight}">'
            f'<span class="lb-pos">{medal}</span>'
            f'<span style="flex:1">{row["avatar"]} {row["name"]}{" (tú)" if is_me else ""}</span>'
            f'<span style="color:{color};font-weight:800;">{sign}{score} pts</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Final screen
# ─────────────────────────────────────────────────────────────────────────────

def _render_final_screen():
    st.markdown(
        "<div class='topic-banner'>"
        "<h1>🏆 ¡Juego finalizado!</h1>"
        "<p>Gracias por participar</p>"
        "</div>",
        unsafe_allow_html=True,
    )
