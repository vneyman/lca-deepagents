PRAGMA foreign_keys = ON;

-- Sources consulted (accessed 2026-09-11):
-- * Billboard Hot 100 artist/chart data, summarized in the Neil Diamond discography:
--   https://en.wikipedia.org/wiki/Neil_Diamond_discography
-- * Library of Congress, The Songs of Billy Joel (chart peaks and album track lists):
--   https://www.loc.gov/static/events/gershwin-prize/documents/2014-joel-program.pdf
-- * American Songwriter, Billboard Hot 100 No. 1 history for Neil Diamond:
--   https://americansongwriter.com/on-this-day-in-1970-neil-diamond-topped-the-billboard-hot-100-for-the-first-time-with-cracklin-rosie/
-- * ChartMasters album-sales estimates (used for approximate worldwide pure sales):
--   https://chartmasters.org/neil-diamond-albums-and-songs-sales/
--   https://chartmasters.org/cspc-billy-joel-popularity-analysis/
-- * Billy Joel official RIAA certification cross-check:
--   https://www.billyjoel.com/timeline/
-- Chart year is the year of the listed Hot 100 peak; is_hit means a Top 20 Hot 100 single.
-- copies_sold is an approximate worldwide pure-album-sales estimate, not an audit figure.

INSERT INTO t_artist (id, name_first, name_last, date_born) VALUES
    (1, 'Neil', 'Diamond', '1941-01-24'),
    (2, 'Billy', 'Joel', '1949-05-09');

INSERT INTO t_song (id, artist_id, name, chart_year, is_hit, highest_ranking) VALUES
    (1, 1, 'Cherry, Cherry', 1966, 1, 6),
    (2, 1, 'Sweet Caroline', 1969, 1, 4),
    (3, 1, 'Holly Holy', 1969, 1, 6),
    (4, 1, 'Cracklin'' Rosie', 1970, 1, 1),
    (5, 1, 'I Am... I Said', 1971, 1, 4),
    (6, 1, 'Song Sung Blue', 1972, 1, 1),
    (7, 1, 'Longfellow Serenade', 1974, 1, 5),
    (8, 1, 'If You Know What I Mean', 1976, 1, 11),
    (9, 1, 'You Don''t Bring Me Flowers', 1978, 1, 1),
    (10, 1, 'Desirée', 1978, 1, 16),
    (11, 2, 'Piano Man', 1974, 0, 25),
    (12, 2, 'Say Goodbye to Hollywood', 1976, 1, 17),
    (13, 2, 'Just the Way You Are', 1977, 1, 3),
    (14, 2, 'Movin'' Out (Anthony''s Song)', 1977, 1, 17),
    (15, 2, 'My Life', 1978, 1, 3),
    (16, 2, 'She''s Always a Woman', 1978, 1, 17),
    (17, 2, 'Big Shot', 1979, 1, 14),
    (18, 2, 'You May Be Right', 1980, 1, 7),
    (19, 2, 'It''s Still Rock and Roll to Me', 1980, 1, 1),
    (20, 2, 'Uptown Girl', 1983, 1, 3);

INSERT INTO t_album (id, name, date_release, copies_sold) VALUES
    (1, 'The Feel of Neil Diamond', '1966-08-01', 100000),
    (2, 'Brother Love''s Travelling Salvation Show', '1969-05-01', 1112500),
    (3, 'Touching You, Touching Me', '1969-11-01', 1780000),
    (4, 'Tap Root Manuscript', '1970-11-01', 2685000),
    (5, 'Stones', '1971-04-01', 2210000),
    (6, 'Moods', '1972-07-01', 3342500),
    (7, 'Serenade', '1974-10-01', 3877500),
    (8, 'Beautiful Noise', '1976-06-11', 4865000),
    (9, 'You Don''t Bring Me Flowers', '1978-11-01', 4127500),
    (10, 'Piano Man', '1973-11-09', 6700000),
    (11, 'Turnstiles', '1976-05-19', 2900000),
    (12, 'The Stranger', '1977-09-29', 15300000),
    (13, '52nd Street', '1978-10-12', 13300000),
    (14, 'Glass Houses', '1980-03-10', 11000000),
    (15, 'An Innocent Man', '1983-08-08', 13000000);

INSERT INTO t_album_song (album_id, song_id, track_number) VALUES
    (1, 1, NULL),
    (2, 2, NULL),
    (3, 3, NULL),
    (4, 4, 1),
    (5, 5, NULL),
    (6, 6, 1),
    (7, 7, 1),
    (8, 8, 1),
    (9, 9, 1),
    (9, 10, 2),
    (10, 11, 1),
    (11, 12, 1),
    (12, 13, 4),
    (12, 14, 1),
    (13, 15, 1),
    (13, 16, 3),
    (13, 17, 1),
    (14, 18, 1),
    (14, 19, 2),
    (15, 20, 4);
