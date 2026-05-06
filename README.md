# 🎮 MiniGames Competition

Una aplicación web de competición de minijuegos multijugador construida con Streamlit.

## 📋 Descripción

Plataforma de competición con **3 minijuegos** jugados en rondas, con sistema de apuesta doble y clasificaciones históricas.

### 🎯 Minijuegos

| # | Nombre | Descripción | Puntuación |
|---|--------|-------------|------------|
| 1 | **Ordena como puedas** | Ordena 4 elementos correctamente | 4 aciertos=+10, 2=+5, 1=-5, 0=0 |
| 2 | **¿Qué prefieres?** | Elige la opción más votada | Mayoría=+10, Minoría=-10 |
| 3 | **¿Quién se acerca más?** | Adivina un número absurdo | Fórmula proporcional por cercanía |

### 💰 Sistema de apuesta doble

Antes de cada ronda los jugadores pueden elegir multiplicar su puntuación (positiva o negativa) por ×2.

---

## 🚀 Despliegue en Streamlit Community Cloud

### 1. Sube el proyecto a GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/minigames
git push -u origin main
```

### 2. Despliega en Streamlit Community Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio y `app.py` como entry point
4. Haz clic en **Deploy**

### 3. Configurar base de datos persistente (importante)

Streamlit Community Cloud **resetea el sistema de archivos** en cada deploy. Para datos persistentes usa:

**Opción A — Streamlit Secrets + SQLite (para pruebas):**
El archivo `minigames.db` se perderá en cada deploy. Solo válido para una sesión.

**Opción B — PostgreSQL en Supabase (recomendado para producción):**

1. Crea una cuenta gratuita en [supabase.com](https://supabase.com)
2. Crea un nuevo proyecto y obtén la connection string
3. En Streamlit Community Cloud → Settings → Secrets, añade:
   ```toml
   [database]
   url = "postgresql://user:password@host:5432/dbname"
   ```
4. Actualiza `utils/database.py` para usar psycopg2 con la URL de secrets

---

## 💻 Ejecución local

```bash
pip install -r requirements.txt
streamlit run app.py
```

### URLs de acceso:
- **Página principal:** `http://localhost:8501`
- **Panel admin:** `http://localhost:8501/?view=admin`
- **Vista jugadores:** `http://localhost:8501/?view=play`

---

## 📱 Flujo de una partida

### Administrador:
1. ⚙️ **Configuración** → Crear nueva edición (con plantilla o personalizada)
2. 🎮 **Control** → Seleccionar edición → Iniciar competición
3. Por cada ronda:
   - `📢 Anunciar temática` → Los jugadores ven de qué va
   - `💰 Abrir apuestas` → Los jugadores deciden si apuestan ×2
   - `▶️ Iniciar ronda` → Los jugadores responden
   - `⏹️ Cerrar ronda` → Se calculan puntuaciones automáticamente
4. 📊 **Puntuaciones** → Ver clasificaciones en tiempo real

### Jugadores:
1. Acceden a la URL desde su móvil con `?view=play`
2. Introducen su nombre y eligen avatar
3. Esperan en el lobby
4. Por cada ronda: ven la temática → apuestan → responden → ven resultados

---

## 🗃️ Estructura del proyecto

```
minigames/
├── app.py                  # Entry point con routing
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Tema y configuración
├── pages/
│   ├── admin.py            # Panel de administrador
│   └── player.py           # Vista de jugadores (móvil)
└── utils/
    ├── database.py         # SQLite ORM completo
    ├── scoring.py          # Motor de puntuación de los 3 juegos
    ├── game_data.py        # Plantillas de rondas predefinidas
    └── styles.py           # CSS global
```

---

## 📊 Esquema de base de datos

```sql
editions      -- Cada competición/año
players       -- Jugadores por edición  
games         -- 3 juegos por edición
rounds        -- Rondas dentro de cada juego
player_round_choices  -- Respuestas y apuestas de cada jugador
scores        -- Puntuaciones calculadas (histórico permanente)
```

---

## 🎨 Personalización

### Editar rondas predefinidas
Modifica el archivo `utils/game_data.py` para cambiar las preguntas de la plantilla.

### Migrar a PostgreSQL
Cambia en `utils/database.py`:
```python
import psycopg2
DB_URL = st.secrets["database"]["url"]

def get_connection():
    return psycopg2.connect(DB_URL)
```
Y adapta la sintaxis SQL (sustituye `?` por `%s` en las queries).
