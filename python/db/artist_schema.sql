PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS t_album_song;
DROP TABLE IF EXISTS t_album;
DROP TABLE IF EXISTS t_song;
DROP TABLE IF EXISTS t_artist;

CREATE TABLE t_artist (
    id INTEGER PRIMARY KEY,
    name_first TEXT NOT NULL,
    name_last TEXT NOT NULL,
    date_born TEXT NOT NULL,
    UNIQUE (name_first, name_last)
);

CREATE TABLE t_song (
    id INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL REFERENCES t_artist(id),
    name TEXT NOT NULL,
    chart_year INTEGER NOT NULL CHECK (chart_year BETWEEN 1950 AND 2100),
    is_hit INTEGER NOT NULL DEFAULT 0 CHECK (is_hit IN (0, 1)),
    highest_ranking INTEGER NOT NULL CHECK (highest_ranking BETWEEN 1 AND 100),
    UNIQUE (artist_id, name)
);

CREATE TABLE t_album (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    date_release TEXT NOT NULL,
    copies_sold INTEGER CHECK (copies_sold IS NULL OR copies_sold >= 0)
);

CREATE TABLE t_album_song (
    album_id INTEGER NOT NULL REFERENCES t_album(id) ON DELETE CASCADE,
    song_id INTEGER NOT NULL REFERENCES t_song(id) ON DELETE CASCADE,
    track_number INTEGER CHECK (track_number IS NULL OR track_number > 0),
    PRIMARY KEY (album_id, song_id)
);

CREATE INDEX idx_song_artist_chart ON t_song (artist_id, chart_year, highest_ranking);
CREATE INDEX idx_album_song_song ON t_album_song (song_id);
