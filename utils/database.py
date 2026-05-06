import sqlite3
import json
import os
from utils.game_data import GAME_TEMPLATES


DB_PATH = os.path.join(os.path.dirname(__file__), "minigames.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    
    # 1. Cerrar conexiones previas
    try:
        conn = get_connection()
        conn.close()
    except:
        pass

    # 2. Borrar la DB si no está bloqueada
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
    except PermissionError:
        print("DB bloqueada, no se puede borrar ahora")
        return
        
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""

    -- 1. Jugadores (El score es la suma de sus scores en la tabla de puntos)
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            avatar TEXT DEFAULT '🎮'
        );

    -- 2. Juegos 
        CREATE TABLE IF NOT EXISTS games (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        );
        
    -- 3. Rondas
        CREATE TABLE IF NOT EXISTS rounds (
            round_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            topic TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_answer TEXT,
            status TEXT DEFAULT 'announcing',
            FOREIGN KEY (game_id) REFERENCES games(game_id)
        );

    -- 4. Respuestas y apuestas del momento    
        CREATE TABLE IF NOT EXISTS answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            game_id,
            round_id INTEGER NOT NULL,
            double_bet INTEGER DEFAULT 0,
            answer TEXT,
            UNIQUE(player_id, round_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (round_id) REFERENCES rounds(round_id)
        );

    --5.  Puntos acumulados
        CREATE TABLE IF NOT EXISTS scores (
            score_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            game_id INTEGER NOT NULL,
            round_id INTEGER NOT NULL,
            final_score INTEGER DEFAULT 0,
            UNIQUE(player_id,game_id ,round_id),
            
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (game_id) REFERENCES games(game_id),
            FOREIGN KEY (round_id) REFERENCES rounds(round_id)
        );
    """)

    conn.commit()
    conn.close()


# ── Player ──────────────────────────────────────────────────

def add_player(name: str, avatar: str = "🎮"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO players (name, avatar) VALUES (?, ?)", (name, avatar))        
    player_id = c.lastrowid
    conn.commit()
    conn.close()
    return player_id


def get_player(player_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM players WHERE player_id=?", (player_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_players():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM players").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Games ─────────────────────────────────────────────────────────────────────

def update_game_status(game_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE games SET status=? WHERE game_id=?", (status, game_id))
    conn.commit()
    conn.close()


def get_game(game_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM games WHERE game_id=?", (game_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_games():
    conn = get_connection()
    row = conn.execute("SELECT * FROM games ").fetchall()
    conn.close()
    return [dict(r) for r in row]

def get_current_game():
    conn = get_connection()
    cur = conn.execute("SELECT * FROM games WHERE status = 'active' LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row

# ── Rounds ────────────────────────────────────────────────────────────────────

def get_round(round_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM rounds WHERE round_id=?", (round_id,)).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["options"] = json.loads(d["options"])
    return d

def get_all_rounds(game_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM rounds WHERE game_id=?", (game_id,)).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["options"] = json.loads(d["options"])
        result.append(d)
    return result

def get_active_round_for_game(game_id):
    conn = get_connection()
    cur = conn.execute("""
        SELECT * FROM rounds
        WHERE game_id = ? AND status = 'active'
        LIMIT 1
    """, (game_id,))
    row = cur.fetchone()
    conn.close()
    return row

def update_round_status(round_id: int, status: str):
    conn = get_connection()
    # Simplificado: No guardamos tiempos de inicio/fin si no los usas para historial
    conn.execute("UPDATE rounds SET status=? WHERE round_id=?", (status, round_id))
    conn.commit()
    conn.close()

def set_round_correct_answer(round_id: int, correct_answer: str):
    conn = get_connection()
    conn.execute("UPDATE rounds SET correct_answer=? WHERE round_id=?", (correct_answer, round_id))
    conn.commit()
    conn.close()


# ── Bets ────────────────────────────────────────────────────────────

def submit_double_bet(player_id: int, round_id: int, double_bet: bool):
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO answers (player_id, round_id, double_bet)
        VALUES (?, ?, ?)
        ON CONFLICT(player_id, round_id) DO UPDATE SET 
            double_bet = excluded.double_bet
        """,
        (player_id, round_id, int(double_bet)),
    )
    conn.commit()
    conn.close()

# ── Answers ────────────────────────────────────────────────────────────

def submit_answer(player_id: int, round_id: int,answer: str):
    """Fusionado: Envía respuesta y apuesta en una sola función."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO answers (player_id, round_id, answer)
           VALUES (?,?,?)
           ON CONFLICT(player_id, round_id) DO UPDATE SET 
           answer=excluded.answer""",
        (player_id, round_id,answer),
    )
    conn.commit()
    conn.close()


def get_round_answers(round_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT a.*, p.name, p.avatar 
           FROM answers a
           JOIN players p ON p.player_id = a.player_id
           WHERE a.round_id=?""",
        (round_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_player_choice(player_id: int, round_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM answers WHERE player_id=? AND round_id=?" ,
        (player_id, round_id),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def count_answers_submitted(round_id: int):
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as c FROM answers WHERE round_id=? AND answer IS NOT NULL",
        (round_id,),
    ).fetchone()
    conn.close()
    return row["c"] if row else 0


# ── Scores ────────────────────────────────────────────────────────────────────

def save_score(player_id: int, round_id: int, game_id: int, final_score: int):
    conn = get_connection()
    conn.execute(
        """INSERT INTO scores (player_id, round_id, game_id, final_score)
           VALUES (?,?,?,?)
           ON CONFLICT(player_id, game_id ,round_id) DO UPDATE SET
             final_score=excluded.final_score""",
        (player_id, round_id, game_id,final_score),
    )
    conn.commit()
    conn.close()

#Clasificación actual 
def get_leaderboard():
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.player_id, p.name, p.avatar, COALESCE(SUM(s.final_score), 0) as total_score
           FROM players p
           LEFT JOIN scores s ON p.player_id=s.player_id
           GROUP BY p.player_id
           ORDER BY total_score DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_game_leaderboard(game_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.player_id, p.name, p.avatar, COALESCE(SUM(s.final_score), 0) as game_score
           FROM players p
           LEFT JOIN scores s ON s.player_id=p.player_id AND s.game_id=?
          
           GROUP BY p.player_id, p.name, p.avatar
           ORDER BY game_score DESC""",
        (game_id),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_round_scores(round_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.*, p.name, p.avatar FROM scores s
           JOIN players p ON p.player_id=s.player_id
           WHERE s.round_id=?
           ORDER BY s.final_score DESC""",
        (round_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]



# ── State helpers (for admin state machine) ───────────────────────────────────

#Devuelve los datos de la utlima ronda de la BBDD
def get_active_round():
    """Retorna la ronda actual activa de cualquier juego."""
    conn = get_connection()
    row = conn.execute(
        """SELECT r.* FROM rounds r
           WHERE r.status IN ('announcing','betting','active','results')
           ORDER BY r.roun_id DESC LIMIT 1"""
    ).fetchone()
    conn.close()
    if not row: return None
    d = dict(row)
    d["options"] = json.loads(d["options"])
    return d


#-------------------------------Cargamos los juegos y rondas en la bbdd
def seed_games_and_rounds():
    conn = get_connection()
    
    # Borrar juegos anteriores
    conn.execute("DELETE FROM rounds")
    conn.execute("DELETE FROM games")
    
    cur = conn.execute("SELECT COUNT(*) FROM games")
    
    count = cur.fetchone()[0]

    # Solo evitar duplicados si REALMENTE hay juegos
    if count > 0:
        print("DEBUG: Ya hay juegos, no cargo nada")
        conn.close()
        return

    for game in GAME_TEMPLATES:
        # Insertar juego
        cur = conn.execute(
            "INSERT INTO games (title, status) VALUES (?, 'pending')",
            (game["title"],)
        )
        game_id = cur.lastrowid

        # Insertar rondas
        for i, rnd in enumerate(game["rounds"], start=1):
            conn.execute(
                """
                INSERT INTO rounds (game_id, round_number, topic, question, options, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    game_id,
                    i,
                    rnd["topic"],
                    rnd["question"],
                    json.dumps(rnd["options"]),
                    rnd["correct_answer"],
                )
            )

    conn.commit()
    conn.close()