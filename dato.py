import sqlite3
import json
import pprint
import batosql

pp = pprint.PrettyPrinter()
conn = sqlite3.connect('tmp/bato.sqlite')
conn.execute("PRAGMA foreign_keys=ON;")
hash_of_tables = {
    'mangas': 'id integer PRIMARY KEY, name text UNIQUE NOT NULL,\
 link text NOT NULL',
    'genres': 'id integer PRIMARY KEY, name text UNIQUE NOT NULL',
    'authors': 'id integer PRIMARY KEY, name text UNIQUE NOT NULL',
    'artists': 'id integer PRIMARY KEY, name text UNIQUE NOT NULL',
}
for table, columns in hash_of_tables.items():
    conn.execute(batosql.create_table_query.format(table, columns))

list_of_indexes = [
]
for index in list_of_indexes:
    conn.execute(batosql.create_index_query.format(*index))

list_of_join_tables = [
    ('mangas', 'genres'),
    ('mangas', 'authors'),
    ('mangas', 'artists'),
]
for join_table in list_of_join_tables:
    batosql.create_join_table(conn, *join_table)

conn.commit()

follows_file = open("tmp/batofollows.json", "r")
follows_json = json.load(follows_file)

mangas_file = open("tmp/batomanga.json", "r")
mangas_json = json.load(mangas_file)

grouped_mangas = {}
for x in mangas_json:
    grouped_mangas.update({x['name']: x})
grouped_follows = {}
for x in follows_json:
    grouped_follows.update({x['name']: x})
for manga in mangas_json:
    grouped_mangas[manga['name']].update(grouped_follows[manga['name']])
# grouped_mangas: { name: , link: , genres: }


def populate_manga():

    for manga in grouped_mangas.values():
        batosql.insert_into(conn, 'mangas',
                            ['name', 'link'], (manga['name'], manga['link']))

    for manga in grouped_mangas.values():
        for genre in manga['genres']:
            batosql.insert_into(conn, 'genres', 'name', genre)

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
