from inflection import *
create_table_query = "CREATE TABLE IF NOT EXISTS {0}({1})"
create_index_query = "CREATE INDEX IF NOT EXISTS {0} ON {1}({2})"
insert_query = "INSERT OR REPLACE INTO {0}({columns}) VALUES({values})"
associate_many_to_many_query = "\
INSERT OR IGNORE INTO {join_tbl}({first}_id, {second}_id)\
SELECT a.id, b.id\
FROM\
    {first_tbl} as a,\
    {second_tbl} as b\
WHERE\
    NOT EXISTS (\
    SELECT ab.{first}_id, ab.{second}_id\
    FROM {join_tbl} as ab\
    WHERE ab.{first}_id = a.id\
    AND ab.{second}_id = b.id\
    )\
    AND a.{first_col} = ?\
    AND b.{second_col} = ?\
"


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
        return x if type(x) is unicode else unicode(x, 'utf-8', errors='strict')


def insert_into(db, table, columns, values, many=False):
    if many:
        iter_list = (x for x in enumerate(values) if type(x) in (tuple, list))
        many_list = next(iter_list, None)
        if many_list is None:
            raise ValueError("Many queries need one list")
        if next(iter_list, None) is not None:
            raise ValueError("Many queries need exactly one list")

    values = process_values_for_insert(values)
    columns = serialize(columns)
    qmarks = '?'
    for _ in xrange(len(values) - 1):
        qmarks += ', ?'
    if many:
        query_objects = (values[:many_list - 1] + (obj, ) +
                         values[many_list + 1:] for obj in values[many_list])
        db.executemany(insert_query.format(
            table, columns=columns, values=qmarks
        ), query_objects)
    else:
        db.execute(insert_query.format(
            table, columns=columns, values=qmarks
        ), values)
    db.commit()

    def process_values_for_insert(values):
        if type(values) is not tuple:
            if type(values) is str:
                return (unicode(values, 'utf-8', errors='strict'), )
            elif type(values) is unicode:
                return values
            else:
                return tuple(values)


def get_many_to_many_query(first_tbl, second_tbl, first_col, second_col):
    first = singularize(first_tbl)
    second = singularize(second_tbl)
    join_tbl = first_tbl + '_' + second_tbl
    return associate_many_to_many_query.format(join_tbl=join_tbl,
                                               first_tbl=first_tbl,
                                               second_tbl=second_tbl,
                                               first=first,
                                               second=second,
                                               first_col=first_col,
                                               second_col=second_col)
