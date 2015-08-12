import sqlite3
conn = sqlite3.connect('bato.db')
create_query = "CREATE TABLE IF NOT EXISTS {0}({1})"
mangas_table = ('mangas', 'id integer, name text')
mangas_genres_table = ('mangas_genres_table', 'id integer,\
 manga_id integer, genre_id integer')
genres_table = ('genres_table', 'id integer, name text')
for table in [mangas_table, mangas_genres_table, genres_table]:
    conn.execute(create_query.format(*table))
conn.commit()
