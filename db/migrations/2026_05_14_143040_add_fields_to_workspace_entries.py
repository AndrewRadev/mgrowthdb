import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE WorkspaceEntries
        ADD dataType VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD subjectType VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD subjectId INT DEFAULT NULL,
        ADD units VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE WorkspaceEntries
        DROP dataType,
        DROP subjectType,
        DROP subjectId,
        DROP units;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
