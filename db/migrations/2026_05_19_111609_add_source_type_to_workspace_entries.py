import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE WorkspaceEntries
        ADD sourceType VARCHAR(100) NOT NULL COLLATE utf8mb4_bin DEFAULT "upload";
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE WorkspaceEntries
        DROP sourceType;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
