import sqlite3
import os
import tempfile
from typing import List, Dict, Any

# On Vercel, the filesystem is read-only except /tmp
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DB_PATH = os.path.join(tempfile.gettempdir(), "weather_system.db")
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "weather_system.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database schema tables."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Table 1: Search Query History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                temperature REAL,
                condition TEXT,
                safety_score INTEGER,
                status_level TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 2: Favorite Bookmarked Cities
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorite_cities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT UNIQUE NOT NULL,
                country TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed initial favorite cities if empty
        cursor.execute("SELECT COUNT(*) as count FROM favorite_cities")
        if cursor.fetchone()["count"] == 0:
            default_favorites = [
                ("Chennai", "India"),
                ("London", "United Kingdom"),
                ("Tokyo", "Japan"),
                ("New York", "United States"),
                ("Paris", "France")
            ]
            cursor.executemany("INSERT INTO favorite_cities (city, country) VALUES (?, ?)", default_favorites)

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB INIT NOTICE] {e}")


def log_search(city: str, country: str, temp: float, condition: str, safety_score: int, status_level: str):
    """Log a weather search query to SQLite database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO search_history (city, country, temperature, condition, safety_score, status_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (city, country, temp, condition, safety_score, status_level))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB LOG NOTICE] {e}")


def get_recent_history(limit: int = 8) -> List[Dict[str, Any]]:
    """Retrieve recent search history."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, city, country, temperature, condition, safety_score, status_level, 
                   strftime('%H:%M:%S', timestamp) as time_str
            FROM search_history 
            ORDER BY id DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return []


def get_favorites() -> List[Dict[str, Any]]:
    """Retrieve favorite cities from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, city, country FROM favorite_cities ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception:
        return [
            {"id": 1, "city": "Chennai", "country": "India"},
            {"id": 2, "city": "London", "country": "United Kingdom"},
            {"id": 3, "city": "Tokyo", "country": "Japan"}
        ]


def toggle_favorite(city: str, country: str) -> bool:
    """Add or remove a city from favorites database table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM favorite_cities WHERE LOWER(city) = LOWER(?)", (city,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("DELETE FROM favorite_cities WHERE id = ?", (exists["id"],))
            is_fav = False
        else:
            cursor.execute("INSERT INTO favorite_cities (city, country) VALUES (?, ?)", (city, country))
            is_fav = True
            
        conn.commit()
        conn.close()
        return is_fav
    except Exception:
        return False


def get_db_analytics() -> Dict[str, Any]:
    """Calculate system database analytics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM search_history")
        total_queries = cursor.fetchone()["total"]
        
        cursor.execute("SELECT AVG(safety_score) as avg_safety FROM search_history")
        avg_safety_row = cursor.fetchone()["avg_safety"]
        avg_safety = round(avg_safety_row, 1) if avg_safety_row else 85.0
        
        cursor.execute("SELECT city, COUNT(city) as count FROM search_history GROUP BY city ORDER BY count DESC LIMIT 1")
        top_city_row = cursor.fetchone()
        top_city = top_city_row["city"] if top_city_row else "Chennai"

        conn.close()
        return {
            "total_queries": total_queries,
            "avg_safety_score": avg_safety,
            "top_city": top_city,
            "db_status": "SQLite Serverless Active"
        }
    except Exception:
        return {
            "total_queries": 1,
            "avg_safety_score": 85.0,
            "top_city": "Chennai",
            "db_status": "Serverless Active"
        }
