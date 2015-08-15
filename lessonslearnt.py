# NOTE: alter table practice to change constraints on a table in SQLITE
turn_off_foreign_key = '''PRAGMA foreign_keys=OFF'''

alter_join_table = '''
CREATE TABLE IF NOT EXISTS mangas_genres_x
    (
    manga_id INTEGER NOT NULL REFERENCES mangas(id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (manga_id, genre_id)
    )
'''
remember_indexes = '''
CREATE TABLE IF NOT EXISTS vars (type TEXT, sql TEXT);
INSERT INTO vars
    SELECT type, sql
    FROM sqlite_master
    WHERE tbl_name='mangas_genres';
'''

migrate_table = '''
INSERT INTO mangas_genres_x SELECT manga_id, genre_id FROM mangas_genres
'''

drop_old = '''
DROP TABLE mangas_genres
'''

rename_new = '''
ALTER TABLE mangas_genres_x RENAME TO mangas_genres
'''

drop_vars_table = '''
DROP TABLE vars;
'''

list_of_sql = [turn_off_foreign_key, alter_join_table, remember_indexes,
               migrate_table, drop_old, rename_new, drop_vars_table]

for sql in list_of_sql:
    conn.executescript(sql)
