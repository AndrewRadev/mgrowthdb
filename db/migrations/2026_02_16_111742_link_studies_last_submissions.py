import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Submissions
        ADD publishedAt datetime DEFAULT NULL
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Studies
        ADD lastSubmissionId int DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Studies
        DROP lastSubmissionId
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Submissions
        DROP publishedAt
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
