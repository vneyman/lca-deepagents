# TODO

Create a sqllite database in `@python/db/artist.db`

# Schema

## Tables
- include in `artist_schema.sql`
- artist
    - id
    - name_first
    - name_last
    - date_born
- song 
    - id
    - artist_id
    - name
    - is_hit
    - highest_ranking
- album
    - id
    - song_id
    - name
    - date_release
    - copies_sold

## Table Description and Seed Data 

### Description 
- artist: focus on 2 musicians: Neil Diamond and Billy Joel 
- song: top 10 songs for each artist
- album: album for each song

### Seed Data 
- populate from reputable sources via web search 
- include in `artist_seed.sql`

## Scripts

.sql files should create the database. Test creating. Should be able to answer questions below by querying the database:
Q1: What were Neil Diamonds top 3 songs in 1970s?
Q2: did Neil Diamon and Joel ever have a top 20 single during same year?