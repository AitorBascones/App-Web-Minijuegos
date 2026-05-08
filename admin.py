import streamlit as st
import time
from utils.database import *
from utils.scoring import score_game1, score_game2, score_game3
from utils.game_data import ROUND_DURATIONS

# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def render_leaderboard(rows, title="🏆 Clasificación"):
    st.markdown(f"### {title}")
    medals = ["🥇", "🥈", "🥉"]
    for i, row in enumerate(rows):
        medal = medals[i] if i < 3 else f"{i+1}."
        score = row.get("total_score", row.get("game_score", 0))
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; padding:5px; border-bottom:1px solid #eee;">'
            f'<span>{medal} {row["avatar"]} {row["name"]}</span>'
            f'<b>{score} pts</b></div>',
            unsafe_allow_html=True
        )
def get_last_round_number(game_id):
    conn = get_connection()
    cur = conn.execute("SELECT MAX(round_number) FROM rounds WHERE game_id = ?", (game_id,))
    val = cur.fetchone()[0]
    conn.close()
    return val

# ─────────────────────────────────────────────────────────────────────────────
# MAIN ADMIN RENDER
# ─────────────────────────────────────────────────────────────────────────────

def render_admin():
    st.title("🔧 Control de Partida")
    
    # Botón para cargar juegos desde game_data.py
    if st.sidebar.button("📥 Cargar juegos de ejemplo"):
        seed_games_and_rounds()
        st.success("Juegos cargados correctamente")
        st.rerun()

    # Obtener todos los juegos
    games = get_all_games()
    if not games:
        st.warning("No hay juegos creados.")
        st.stop()
    
    # Juegos controlables: activos primero (para no perderlos tras "Iniciar"), luego pendientes
    controllable_games = (
        [g for g in games if g["status"] == "active"] +
        [g for g in games if g["status"] == "pending"]
    )

    # Solo mostrar la pantalla final cuando TODOS los juegos estén finalizados
    if not controllable_games:
        lb = get_leaderboard()
        render_leaderboard(lb, "🏆 Clasificación Final")
        st.sidebar.success("🎉 Todos los juegos han sido completados")
        st.stop()
    
    # Selección de juego
    game_options = {g["title"]: g["game_id"] for g in controllable_games}
    sel_game = st.sidebar.selectbox("Seleccionar Juego", list(game_options.keys()))
    game_id = game_options[sel_game]
    st.sidebar.caption("👑 Panel del Señor Vascones")

    tab_control, tab_leaderboard = st.tabs(["🎮 Flujo de Juego", "📊 Clasificación"])
    
    # ════════════════════════════════════════════════════════════════════════
    # TAB: CONTROL DE PARTIDA
    # ════════════════════════════════════════════════════════════════════════
    with tab_control:
        game = get_game(game_id)
        players = get_all_players()
        rounds = get_all_rounds(game_id)

        # Estado General
        col1, col2 = st.columns(2)
        col1.metric("Jugadores", len(players))
        col2.markdown(f"**Estado:** `{game['status'].upper()}`")

        if game["status"] == "pending":
            if st.button("▶️ Iniciar Juego", type="primary", use_container_width=True):
                update_game_status(game_id, "active")
                st.rerun()
                
        st.divider()

        # Control de rondas
        for rnd in rounds:
            _render_round_simple_control(rnd, rounds)

        if game["status"] == "active":
            if st.button("🏁 Finalizar Juego", use_container_width=True):
                update_game_status(game_id, "finished")
                st.rerun()
    # ════════════════════════════════════════════════════════════════════════
    # TAB: CLASIFICACIÓN
    # ════════════════════════════════════════════════════════════════════════
    with tab_leaderboard:
        lb = get_leaderboard()
        render_leaderboard(lb, f"Ranking: {sel_game}")

        st.divider()
        g = get_game(game_id)
        showing = bool(g.get("show_leaderboard", 0))
        if showing:
            st.success("📊 Clasificación visible para los jugadores")
            if st.button("❌ Ocultar clasificación", use_container_width=True):
                set_game_show_leaderboard(game_id, 0)
                st.rerun()
        else:
            if st.button("📊 Enviar clasificación a jugadores", type="primary", use_container_width=True):
                set_game_show_leaderboard(game_id, 1)
                st.rerun()

        if st.button("🔄 Actualizar Datos"):
            st.rerun()

    # Auto-refresh: 1s while a round is active (timer), 3s otherwise (lobby/betting)
    game_now = get_game(game_id)
    all_rounds = get_all_rounds(game_id)
    if any(r["status"] == "active" for r in all_rounds):
        time.sleep(1)
        st.rerun()
    elif game_now["status"] == "pending" or any(r["status"] == "betting" for r in all_rounds):
        time.sleep(3)
        st.rerun()


def _render_round_simple_control(rnd, all_rounds):
    st.markdown(f"**Ronda {rnd['round_number']}: {rnd['topic']}**")

    status = rnd["status"]
    total_p = len(get_all_players())

    # Progreso de apuestas
    if status == "betting":
        bet_count = count_bets_submitted(rnd["round_id"])
        st.write(f"💰 Apuestas: {bet_count} / {total_p}")
        st.progress(bet_count / total_p if total_p > 0 else 0)
        missing = get_players_without_bet(rnd["round_id"])
        if missing:
            names = " · ".join(f"{p['avatar']} {p['name']}" for p in missing)
            st.caption(f"⏳ Sin apostar: {names}")

    # Progreso de respuestas
    if status == "active":
        ans_count = count_answers_submitted(rnd["round_id"])
        st.write(f"✏️ Respuestas: {ans_count} / {total_p}")
        st.progress(ans_count / total_p if total_p > 0 else 0)

        # Tiempo restante de la ronda
        started_at = rnd.get("started_at")
        duration = ROUND_DURATIONS.get(rnd["game_id"], 60)
        if started_at:
            start_dt = datetime.datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")
            elapsed = (datetime.datetime.utcnow() - start_dt).total_seconds()
            remaining = max(0, int(duration - elapsed))
            mins, secs = divmod(remaining, 60)
            timer_label = f"{mins:02d}:{secs:02d}"
            if remaining == 0:
                st.error(f"⏱️ Tiempo agotado — {timer_label}")
            elif remaining <= 10:
                st.warning(f"⏱️ Tiempo restante: **{timer_label}**")
            else:
                st.info(f"⏱️ Tiempo restante: **{timer_label}**")

    cols = st.columns(3)

    # 1. Fase de Apuestas
    with cols[0]:
        if status == "announcing":
            any_open = any(r["status"] in ("betting", "active") for r in all_rounds)
            if st.button("💰 Abrir Apuestas", key=f"bet_{rnd['round_id']}", use_container_width=True, disabled=any_open):
                update_round_status(rnd["round_id"], "betting")
                st.rerun()
    
    # 2. Fase de Juego (Activar)
    with cols[1]:
        if status == "betting":
            if st.button("▶️ Empezar Juego", key=f"start_{rnd['round_id']}", type="primary", use_container_width=True):
                update_round_status(rnd["round_id"], "active")
                st.rerun()
    
    # 3. Fase de Cierre y Puntos
    with cols[2]:
        if status == "active" and ans_count == total_p:
            if st.button("⏹️ Cerrar Ronda", key=f"stop_{rnd['round_id']}", use_container_width=True):
                _calculate_scores_internal(rnd)
                update_round_status(rnd["round_id"], "results")
                
                #Si es la ultima ronda se cierra el jeugo
                last_round = get_last_round_number(rnd["game_id"])
                if rnd["round_number"] == last_round:
                    update_game_status(rnd["game_id"], "finished")

                st.rerun()


    st.markdown("---")


def _calculate_scores_internal(rnd):
    
    game_id = rnd["game_id"]

    try:
        if game_id == 1:
            score_game1(rnd["round_id"])
        elif game_id == 2:
            score_game2(rnd["round_id"], game_id)
        elif game_id == 3:
            score_game3(rnd["round_id"])
    except Exception as e:
        st.error(f"Error al puntuar: {e}")