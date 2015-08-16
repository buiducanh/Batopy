from inflection import *
create_table_query = "CREATE TABLE IF NOT EXISTS {0}({1})"
create_index_query = "CREATE INDEX IF NOT EXISTS {0} ON {1}({2})"
insert_query = "INSERT OR REPLACE INTO {0}({columns}) VALUES({values})"


def create_join_table(db, first, second):
    join_table = "{0}_{1}".format(first, second)
    columns = "\
    {2}_id INTEGER NOT NULL REFERENCES {0}(id) ON DELETE CASCADE,\
    {3}_id INTEGER NOT NULL REFERENCES {1}(id) ON DELETE CASCADE,\
    PRIMARY KEY ({2}_id, {3}_id)\
    ".format(first, second,
             singularize(first), singularize(second))
    db.execute(create_table_query.format(join_table, columns))
    db.execute(create_index_query
               .format('ix_{0}'
                       .format(singularize(second)),
                       join_table,
                       '{0}_id'.format(singularize(second))))
    db.commit()


def serialize(x, delimited=False):
    if type(x) is not str and type(x) is not unicode:
        joined = ', '.join(x)
        if type(joined) is not unicode:
            joined = unicode(joined, 'utf-8', errors='strict')
        return joined
    else:
        return x if type(x) is unicode else unicode(x, 'utf-8',errors='strict')


def insert_into(db, table, columns, values):
    columns = serialize(columns)
    qmarks = '?'
    if type(values) is not tuple:
        if type(values) is str:
            values = (unicode(values, 'utf-8', errors='strict'), )
        elif type(values) is unicode:
            return values
        else:
            values = tuple(values)
    for _ in xrange(len(values) - 1):
        qmarks += ', ?'
    db.execute(insert_query.format(
        table, columns=columns, values=qmarks
    ), values)
    db.commit()
