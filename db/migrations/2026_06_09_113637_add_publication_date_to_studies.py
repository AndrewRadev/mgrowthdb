import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Studies
        ADD publicationDate VARCHAR(100),
        ADD INDEX Studies_publicationDate (publicationDate)
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Studies
        DROP INDEX Studies_publicationDate,
        DROP publicationDate
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
