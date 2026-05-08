"""
🎮 MiniGames Competition — Main entry
Streamlit multi-page app with admin and player views.
"""
import streamlit as st
from utils.database import init_db
from utils.styles import GLOBAL_CSS

def run_app():
    # ── Page config ────────────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="Las Vascongadas 🎮",
        page_icon="🎮",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    init_db()
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # ── Route decision ─────────────────────────────────────────────────────────────
    # URL param ?view=admin  → admin panel
    # URL param ?view=play   → player panel (default)

    # Router basado en session_state (fiable)
    if "view" not in st.session_state:
        st.session_state["view"] = "home"
    #st.session_state["view"] = "home"

    view = st.session_state["view"]
    #view="admin"

    if view == "admin":
        if not st.session_state.get("admin_auth"):
            st.markdown("# 🔐 Acceso Administrador")
            pwd = st.text_input("Contraseña", type="password")
            if st.button("Entrar", type="primary"):
                if pwd == "4321":
                    st.session_state["admin_auth"] = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")
            if st.button("← Volver"):
                st.session_state["view"] = "home"
                st.rerun()
        else:
            from admin import render_admin
            render_admin()
    elif view == "play":
        from player import render_player
        render_player()
    else:
        # ── Landing / router ──────────────────────────────────────────────────────
        st.markdown("# 🎮 Las Vascongadas")
        st.markdown("### Bienvenido a la plataforma de competición")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 👨‍💼 ¿Eres el administrador?")
            st.markdown("Gestiona la competición y visualiza las clasificaciones.")
            if st.button("🔧 Panel de Administrador", use_container_width=True, type="primary"):
                st.session_state["view"] = "admin"
                st.rerun()

        with col2:
            st.markdown("#### 🎯 ¿Eres jugador?")
            st.markdown("Únete a la partida y compite con tus amigos.")
            if st.button("🎮 ¡Unirme a jugar!", use_container_width=True,type="primary"):
                st.session_state["view"] = "play"
                st.rerun()

        st.markdown("---")
        st.markdown(
            "<p style='text-align:center;color:rgba(255,255,255,0.4);font-size:0.85rem;'>"
            "Las Vascongadas • Desarrollado por el <b>Señor Vascones</b></p>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    run_app()