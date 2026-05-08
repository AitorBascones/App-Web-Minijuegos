import sqlite3
import json
import os
import datetime
from utils.game_data import GAME_TEMPLATES


DB_PATH = os.path.join(os.path.dirname(__file__), "minigames.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _run_migrations(conn):
    """Aplica migraciones de esquema sin destruir datos existentes."""
    new_columns = [
        "ALTER TABLE answers ADD COLUMN answered_at TEXT",
        "ALTER TABLE rounds ADD COLUMN started_at TEXT",
    ]
    for sql in new_columns:
        try:
            conn.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Columna ya existe

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reactions (
            reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id   INTEGER NOT NULL,
            round_id    INTEGER NOT NULL,
            emoji       TEXT    NOT NULL,
            UNIQUE(player_id, round_id, emoji),
            FOREIGN KEY (player_id) REFERENCES players(player_id),
            FOREIGN KEY (round_id)  REFERENCES rounds(round_id)
        )
    """)
    try:
        conn.execute("ALTER TABLE games ADD COLUMN show_leaderboard INTEGER DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass
    conn.commit()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        avatar    TEXT DEFAULT '🎮'
    );

    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title   TEXT NOT NULL,
        status  TEXT DEFAULT 'pending'
    );

    CREATE TABLE IF NOT EXISTS rounds (
        round_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        game_id      INTEGER NOT NULL,
        round_number INTEGER NOT NULL,
        topic        TEXT NOT NULL,
        question     TEXT NOT NULL,
        options      TEXT NOT NULL,
        correct_answer TEXT,
        status       TEXT DEFAULT 'announcing',
        started_at   TEXT,
        FOREIGN KEY (game_id) REFERENCES games(game_id)
    );

    CREATE TABLE IF NOT EXISTS answers (
        answer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id   INTEGER NOT NULL,
        game_id     INTEGER,
        round_id    INTEGER NOT NULL,
        double_bet  INTEGER DEFAULT 0,
        answer      TEXT,
        answered_at TEXT,
        UNIQUE(player_id, round_id),
        FOREIGN KEY (player_id) REFERENCES players(player_id),
        FOREIGN KEY (game_id)   REFERENCES games(game_id),
        FOREIGN KEY (round_id)  REFERENCES rounds(round_id)
    );

    CREATE TABLE IF NOT EXISTS scores (
        score_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id   INTEGER NOT NULL,
        game_id     INTEGER NOT NULL,
        round_id    INTEGER NOT NULL,
        final_score INTEGER DEFAULT 0,
        UNIQUE(player_id, game_id, round_id),
        FOREIGN KEY (player_id) REFERENCES players(player_id),
        FOREIGN KEY (game_id)   REFERENCES games(game_id),
        FOREIGN KEY (round_id)  REFERENCES rounds(round_id)
    );

    CREATE TABLE IF NOT EXISTS reactions (
        reaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id   INTEGER NOT NULL,
        round_id    INTEGER NOT NULL,
        emoji       TEXT    NOT NULL,
        UNIQUE(player_id, round_id, emoji),
        FOREIGN KEY (player_id) REFERENCES players(player_id),
        FOREIGN KEY (round_id)  REFERENCES rounds(round_id)
    );
    """)

    conn.commit()
    _run_migrations(conn)
    conn.close()


# ── Players ───────────────────────────────────────────────────────────────────

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
    rows = conn.execute("SELECT * FROM players ORDER BY player_id").fetchall()
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
    rows = conn.execute("SELECT * FROM games").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_current_game():
    conn = get_connection()
    row = conn.execute("SELECT * FROM games WHERE status='active' LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


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
    rows = conn.execute(
        "SELECT * FROM rounds WHERE game_id=? ORDER BY round_id", (game_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["options"] = json.loads(d["options"])
        result.append(d)
    return result


def get_active_round_for_player(game_id: int):
    """
    Devuelve la ronda visible para el jugador.
    Si hay alguna ronda en progreso (announcing/betting/active), devuelve la de menor
    round_number (primera sin completar). Si todas están en results, devuelve la más reciente.
    """
    conn = get_connection()
    # Primera ronda aún en juego (más baja = la que hay que jugar ahora)
    row = conn.execute("""
        SELECT * FROM rounds
        WHERE game_id = ? AND status IN ('announcing', 'betting', 'active')
        ORDER BY round_number ASC
        LIMIT 1
    """, (game_id,)).fetchone()

    if not row:
        # Todas completadas: mostrar la ronda de resultados más reciente
        row = conn.execute("""
            SELECT * FROM rounds
            WHERE game_id = ? AND status = 'results'
            ORDER BY round_number DESC
            LIMIT 1
        """, (game_id,)).fetchone()

    conn.close()
    if not row:
        return None
    d = dict(row)
    d["options"] = json.loads(d["options"])
    return d


def update_round_status(round_id: int, status: str):
    conn = get_connection()
    if status == "active":
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE rounds SET status=?, started_at=? WHERE round_id=?",
            (status, now, round_id),
        )
    else:
        conn.execute("UPDATE rounds SET status=? WHERE round_id=?", (status, round_id))
    conn.commit()
    conn.close()


def set_round_correct_answer(round_id: int, correct_answer: str):
    conn = get_connection()
    conn.execute(
        "UPDATE rounds SET correct_answer=? WHERE round_id=?", (correct_answer, round_id)
    )
    conn.commit()
    conn.close()


# ── Bets ──────────────────────────────────────────────────────────────────────

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


# ── Answers ───────────────────────────────────────────────────────────────────

def submit_answer(player_id: int, round_id: int, answer: str):
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO answers (player_id, round_id, answer, answered_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(player_id, round_id) DO UPDATE SET
            answer      = excluded.answer,
            answered_at = COALESCE(answers.answered_at, excluded.answered_at)
        """,
        (player_id, round_id, answer, now),
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
        "SELECT * FROM answers WHERE player_id=? AND round_id=?",
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


def count_bets_submitted(round_id: int):
    """Cuenta jugadores que ya apostaron (tienen cualquier fila en answers para esta ronda)."""
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as c FROM answers WHERE round_id=?",
        (round_id,),
    ).fetchone()
    conn.close()
    return row["c"] if row else 0


def get_players_without_bet(round_id: int):
    """Devuelve los jugadores que aún no han apostado en esta ronda."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.* FROM players p
        WHERE p.player_id NOT IN (
            SELECT a.player_id FROM answers a WHERE a.round_id = ?
        )
        ORDER BY p.player_id
    """, (round_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Scores ────────────────────────────────────────────────────────────────────

def save_score(player_id: int, round_id: int, game_id: int, final_score: int):
    conn = get_connection()
    conn.execute(
        """INSERT INTO scores (player_id, round_id, game_id, final_score)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(player_id, game_id, round_id) DO UPDATE SET
               final_score = excluded.final_score""",
        (player_id, round_id, game_id, final_score),
    )
    conn.commit()
    conn.close()


def get_leaderboard():
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.player_id, p.name, p.avatar,
                  COALESCE(SUM(s.final_score), 0) AS total_score
           FROM players p
           LEFT JOIN scores s ON p.player_id = s.player_id
           GROUP BY p.player_id
           ORDER BY total_score DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_game_show_leaderboard(game_id: int, value: int):
    conn = get_connection()
    conn.execute("UPDATE games SET show_leaderboard=? WHERE game_id=?", (value, game_id))
    conn.commit()
    conn.close()


def get_game_leaderboard(game_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT p.player_id, p.name, p.avatar,
                  COALESCE(SUM(s.final_score), 0) AS game_score
           FROM players p
           LEFT JOIN scores s ON s.player_id = p.player_id AND s.game_id = ?
           GROUP BY p.player_id, p.name, p.avatar
           ORDER BY game_score DESC""",
        (game_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_round_scores(round_id: int):
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.*, p.name, p.avatar,
                  COALESCE(a.double_bet, 0) AS double_bet,
                  a.answered_at
           FROM scores s
           JOIN players p ON p.player_id = s.player_id
           LEFT JOIN answers a ON a.player_id = s.player_id AND a.round_id = s.round_id
           WHERE s.round_id = ?
           ORDER BY s.final_score DESC, a.answered_at ASC""",
        (round_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Reactions ─────────────────────────────────────────────────────────────────

def submit_reaction(player_id: int, round_id: int, emoji: str):
    """Un jugador puede reaccionar con cada emoji una sola vez por ronda."""
    conn = get_connection()
    conn.execute(
        "INSERT OR IGNORE INTO reactions (player_id, round_id, emoji) VALUES (?, ?, ?)",
        (player_id, round_id, emoji),
    )
    conn.commit()
    conn.close()


def get_reactions(round_id: int) -> dict:
    """Devuelve {emoji: count} para la ronda."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT emoji, COUNT(*) AS cnt FROM reactions
           WHERE round_id = ? GROUP BY emoji ORDER BY cnt DESC""",
        (round_id,),
    ).fetchall()
    conn.close()
    return {r["emoji"]: r["cnt"] for r in rows}


# ── State helpers ─────────────────────────────────────────────────────────────

def get_active_round():
    conn = get_connection()
    row = conn.execute(
        """SELECT r.* FROM rounds r
           WHERE r.status IN ('announcing','betting','active','results')
           ORDER BY r.round_id DESC LIMIT 1"""
    ).fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["options"] = json.loads(d["options"])
    return d


def seed_games_and_rounds():
    conn = get_connection()

    conn.execute("DELETE FROM reactions")
    conn.execute("DELETE FROM scores")
    conn.execute("DELETE FROM answers")
    conn.execute("DELETE FROM rounds")
    conn.execute("DELETE FROM games")
    conn.execute("DELETE FROM players")

    for i, game in enumerate(GAME_TEMPLATES, start=1):
        # Forzamos game_id explícito para que siempre sea 1/2/3/4 independientemente
        # del contador AUTOINCREMENT (que no se resetea con DELETE)
        conn.execute(
            "INSERT INTO games (game_id, title, status) VALUES (?, ?, 'pending')",
            (i, game["title"]),
        )

        for j, rnd in enumerate(game["rounds"], start=1):
            conn.execute(
                """INSERT INTO rounds
                       (game_id, round_number, topic, question, options, correct_answer)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    i,
                    j,
                    rnd["topic"],
                    rnd["question"],
                    json.dumps(rnd["options"]),
                    rnd["correct_answer"],
                ),
            )

    conn.commit()
    conn.close()
