from pathlib import Path
import sqlite3


ROOT = Path(__file__).parent
SCHEMA = ROOT / "artist_schema.sql"
SEED = ROOT / "artist_seed.sql"


def connect_seeded() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.executescript(SCHEMA.read_text())
    connection.executescript(SEED.read_text())
    return connection


def test_schema_and_seed_counts() -> None:
    with connect_seeded() as connection:
        assert connection.execute("SELECT COUNT(*) FROM t_artist").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM t_song").fetchone()[0] == 20
        assert connection.execute("SELECT COUNT(*) FROM t_album_song").fetchone()[0] == 20


def test_neil_diamond_top_three_in_the_1970s() -> None:
    with connect_seeded() as connection:
        rows = connection.execute(
            """
            SELECT t_song.name, t_song.highest_ranking
            FROM t_song
            JOIN t_artist ON t_artist.id = t_song.artist_id
            WHERE t_artist.name_first = 'Neil'
              AND t_artist.name_last = 'Diamond'
              AND t_song.chart_year BETWEEN 1970 AND 1979
            ORDER BY t_song.highest_ranking, t_song.name
            LIMIT 3
            """
        ).fetchall()
    assert rows == [
        ("Cracklin' Rosie", 1),
        ("Song Sung Blue", 1),
        ("You Don't Bring Me Flowers", 1),
    ]


def test_artists_had_top_twenty_singles_in_the_same_year() -> None:
    with connect_seeded() as connection:
        rows = connection.execute(
            """
            SELECT DISTINCT neil.chart_year
            FROM t_song AS neil
            JOIN t_song AS joel ON joel.chart_year = neil.chart_year
            JOIN t_artist AS neil_artist ON neil_artist.id = neil.artist_id
            JOIN t_artist AS joel_artist ON joel_artist.id = joel.artist_id
            WHERE neil_artist.name_last = 'Diamond'
              AND joel_artist.name_last = 'Joel'
              AND neil.is_hit = 1
              AND joel.is_hit = 1
            ORDER BY neil.chart_year
            """
        ).fetchall()
    assert rows == [(1976,), (1978,)]
