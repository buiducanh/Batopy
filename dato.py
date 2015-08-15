import sqlite3
import json
import pprint
pp = pprint.PrettyPrinter()
conn = sqlite3.connect('tmp/bato.db')
mangas_table = ('mangas', 'id integer PRIMARY KEY, name text UNIQUE NOT NULL,\
 link text NOT NULL')
genres_table = ('genres', 'id integer PRIMARY KEY, name text UNIQUE NOT NULL')
conn.execute("PRAGMA foreign_keys=ON;")
for table in [mangas_table, genres_table]:
    conn.execute("CREATE TABLE IF NOT EXISTS {0}({1})".format(*table))

create_join_table = '''CREATE TABLE IF NOT EXISTS mangas_genres
    (
    manga_id INTEGER NOT NULL REFERENCES mangas(id) ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (manga_id, genre_id)
    );
    CREATE INDEX IF NOT EXISTS ix_genre  ON mangas_genres(genre_id);
'''
conn.executescript(create_join_table)

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
conn.commit()

follows_file = open("tmp/batofollows.json", "r")
follows_json = json.load(follows_file)

mangas_file = open("tmp/batomanga.json", "r")
mangas_json = json.load(mangas_file)

grouped_mangas = {}
[grouped_mangas.update({x['name']: x}) for x in mangas_json]
grouped_follows = {}
[grouped_follows.update({x['name']: x}) for x in follows_json]
[grouped_mangas[manga['name']].update(grouped_follows[manga['name']])
 for manga in mangas_json]
# grouped_mangas: { name: , link: , genres: }


def populate_manga():

    insert_manga_query = "INSERT OR IGNORE INTO mangas(name, link)\
    VALUES(?, ?)"

    for manga in grouped_mangas.values():
        conn.execute(insert_manga_query, (manga['name'], manga['link']))

    insert_genre_query = '''
    INSERT OR IGNORE INTO genres(name) VALUES(?)
    '''

    for manga in grouped_mangas.values():
        conn.executemany(insert_genre_query,
                         iter(map(lambda x: (x, ), manga['genres'])))

    associate_manga_to_genre_query = '''
    INSERT OR IGNORE INTO mangas_genres(manga_id, genre_id)
    SELECT m.id, g.id
    FROM
        mangas as m,
        genres as g
    WHERE
        NOT EXISTS (
        SELECT mg.manga_id, mg.genre_id
        FROM mangas_genres as mg
        WHERE mg.manga_id = m.id
        AND mg.genre_id = g.id
        )
        AND m.name = ?
        AND g.name = ?
    '''

    for manga in grouped_mangas.values():
        conn.executemany(associate_manga_to_genre_query,
                         iter(map(lambda x: (manga['name'], x),
                                  manga['genres'])))

populate_manga()

conn.commit()

conn.close()
