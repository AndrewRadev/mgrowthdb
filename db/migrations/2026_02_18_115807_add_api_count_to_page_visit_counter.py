import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE PageVisitCounters
        ADD totalApiVisitCount INT NOT NULL DEFAULT 0
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE PageVisitCounters
        DROP totalApiVisitCount
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
