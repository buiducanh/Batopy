import sqlite3
import json
import pprint
import batosql
import pdb

pp = pprint.PrettyPrinter()
conn = sqlite3.connect('tmp/bato.sqlite')
conn.text_factory = sqlite3.OptimizedUnicode
conn.execute("PRAGMA foreign_keys=ON;")
hash_of_tables = {
    'mangas': 'id integer PRIMARY KEY, name text UNIQUE NOT NULL,\
 link text NOT NULL, type text NOT NULL, status text NOT NULL, \
 description text NOT NULL',
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

    attributes_list = ['name', 'link', 'type', 'status', 'description']
    for manga in grouped_mangas.values():
        values = reduce(
            lambda x, y: x + (manga[y], ) if manga[y] is not None else x,
            attributes_list, tuple())
        values = map(batosql.serialize, values)
        batosql.insert_into(conn,
                            'mangas',
                            filter(lambda x: manga[x] is
                                   not None, attributes_list),
                            values)

        for genre in manga['genres']:
            batosql.insert_into(conn, 'genres', 'name', genre)

    associate_manga_to_genre_query = batosql.get_many_to_many_query('mangas',
                                                                    'genres',
                                                                    'name',
                                                                    'name')
    for manga in grouped_mangas.values():
        conn.executemany(associate_manga_to_genre_query,
                         iter(map(lambda x: (manga['name'], x),
                                  manga['genres'])))

populate_manga()

conn.commit()

conn.close()
