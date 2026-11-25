import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Compartments
        MODIFY mediumName varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    # Can't set it to non-null if there are null entries
    pass


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
