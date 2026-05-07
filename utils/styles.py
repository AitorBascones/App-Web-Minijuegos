GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

/* ── 1. Base y Tipografía ──────────────────────────────── */
html, body, .stApp {
    font-family: 'Nunito', sans-serif !important;
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e) !important;
    color: #FFFFFF !important;
}

h1, h2, h3, h4, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Fredoka One', cursive !important;
    color: #FFFFFF !important;
    letter-spacing: 0.5px;
}

/* ── 2. Streamlit Chrome (Limpieza) ─────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 1rem !important; max-width: 900px; }

/* ── 3. INPUTS Y TEXTAREAS (EL FIX QUE BUSCAS) ─────────── */
/* Forzamos el contenedor y el input a ser oscuros con letras blancas brillantes */

div[data-baseweb="input"], div[data-baseweb="base-input"], .stTextInput>div {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 2px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
}

input, textarea, [data-testid="stWidgetInput-TextInput"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background-color: transparent !important;
    font-family: 'Nunito', sans-serif !important;
    font-size: 1.1rem !important;
}

/* Para que el texto no se vuelva negro al hacer click o escribir */
input:focus, textarea:focus {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    outline: none !important;
    border-color: #FF6B6B !important;
}

/* Placeholder (texto guía) en gris claro */
::placeholder, [data-testid="stWidgetInput-TextInput"]::placeholder {
    color: rgba(255, 255, 255, 0.4) !important;
    -webkit-text-fill-color: rgba(255, 255, 255, 0.4) !important;
}

/* ── 4. Widgets (Selectbox, Tabs, Expanders) ───────────── */
.stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 12px !important;
}

.stTabs [data-baseweb="tab"], .st-expanderHeader, .st-expanderHeader p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* ── 5. Botones ────────────────────────────────────────── */
.stButton > button {
    font-family: 'Fredoka One', cursive !important;
    border-radius: 16px;
    transition: all 0.2s ease;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53) !important;
    color: white !important;
    border: none !important;
}

/* ── 6. Componentes de Juego (Cards, Leaderboard) ──────── */
.game-card, .lb-row {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    color: white !important;
    padding: 1rem;
    margin-bottom: 0.5rem;
}

.podium-1 { background: linear-gradient(135deg, #FFD700, #FFA500); color: #1a1a1a !important; }
.podium-2 { background: linear-gradient(135deg, #C0C0C0, #A8A8A8); color: #1a1a1a !important; }
.score-badge { padding: 4px 12px; border-radius: 20px; font-weight: 800; }
.score-positive { background: #00c853; color: white; }

/* ── 7. Fix Global de Texto ────────────────────────────── */
label, p, span, .stMarkdown, .stText, [data-testid="stWidgetLabel"] p {
    color: #FFFFFF !important;
}

/* Forzar que TODOS los botones (incluido el de actualizar) tengan texto blanco */
.stButton > button {
    color: #FFFFFF !important;
    background-color: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

/* Evitar que el texto se vuelva negro al pasar el ratón (hover) */
.stButton > button:hover {
    color: #FFFFFF !important;
    border-color: #FF6B6B !important;
    background-color: rgba(255, 255, 255, 0.2) !important;
}

/* Mantener el estilo especial solo para los Primary (los que ya te funcionan) */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B6B, #FF8E53) !important;
    border: none !important;
    color: white !important;
}

/* ── FIX PARA DESPLEGABLES (EXPANDERS) Y CONTENEDORES ── */

/* ── FIX DEFINITIVO PARA DESPLEGABLES (EXPANDERS) ── */

/* 1. La base del expander: Quitamos cualquier color de fondo heredado */
div[data-testid="stExpander"] {
    background-color: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

/* 2. El encabezado: Bloqueamos el color para que NO cambie nunca */
div[data-testid="stExpander"] summary {
    background-color: rgba(255, 255, 255, 0.05) !important; /* Color fijo */
    color: white !important;
}

/* 3. Forzar el color cuando NO hay cursor y cuando SI lo hay (Igualamos ambos) */
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary:hover,
div[data-testid="stExpander"] summary:focus,
div[data-testid="stExpander"] summary:active {
    background-color: rgba(255, 255, 255, 0.1) !important; /* Mismo color siempre */
    color: white !important;
    outline: none !important;
}

/* 4. Título y flecha: Siempre blancos */
div[data-testid="stExpander"] summary p, 
div[data-testid="stExpander"] svg {
    color: white !important;
    fill: white !important;
}

/* 5. El interior cuando se despliega: Mismo tono oscuro */
div[data-testid="stExpanderDetails"] {
    background-color: rgba(0, 0, 0, 0.15) !important;
    color: white !important;
    border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* 6. Anular cualquier capa de Streamlit que detecte el "brillo" */
div[data-testid="stExpander"] * {
    text-decoration: none !important;
}

/* ── 8. Sidebar Oscuro (MATCH con el resto de la app) ───────────────────── */

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e) !important;
    color: #FFFFFF !important;
    padding: 1.5rem 1rem !important;
    border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
}

/* Texto del sidebar */
[data-testid="stSidebar"] .sidebar-content {
    color: #FFFFFF !important;
    font-family: 'Nunito', sans-serif !important;
    
/* Botones del sidebar */
[data-testid="stSidebar"] button {
    background: rgba(255, 255, 255, 0.1) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] {
    width: 18rem !important;
    min-width: 18rem !important;
}


[data-testid="stSidebar"] button:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    border-color: #FF6B6B !important;
    color: #FFFFFF !important;
}

/* Selectboxes y widgets dentro del sidebar */
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    color: white !important;
}

[data-testid="stSidebar"] input, 
[data-testid="stSidebar"] textarea {
    background-color: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    -webkit-text-fill-color: white !important;
}
</style>
"""