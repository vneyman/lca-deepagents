# Artist database

Create or recreate the SQLite database from the schema and seed scripts:

```bash
cd python/db
sqlite3 artist.db < artist_schema.sql
sqlite3 artist.db < artist_seed.sql
```

The seed contains 10 representative highest-charting Hot 100 singles for
each artist, their associated albums, and the `t_album_song` many-to-many join.

Example queries:

```sql
-- Neil Diamond's three highest-charting songs in the 1970s
SELECT s.name, s.highest_ranking
FROM t_song AS s
JOIN t_artist AS a ON a.id = s.artist_id
WHERE a.name_last = 'Diamond' AND s.chart_year BETWEEN 1970 AND 1979
ORDER BY s.highest_ranking, s.name
LIMIT 3;

-- Years in which both artists had a Top-20 Hot 100 single
SELECT DISTINCT neil.chart_year
FROM t_song AS neil
JOIN t_song AS joel ON joel.chart_year = neil.chart_year
JOIN t_artist AS na ON na.id = neil.artist_id
JOIN t_artist AS ba ON ba.id = joel.artist_id
WHERE na.name_last = 'Diamond' AND ba.name_last = 'Joel'
  AND neil.is_hit = 1 AND joel.is_hit = 1
ORDER BY neil.chart_year;
```
