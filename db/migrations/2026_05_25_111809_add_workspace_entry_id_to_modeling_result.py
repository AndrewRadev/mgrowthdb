import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        ADD workspaceEntryId INT,
        ADD CONSTRAINT ModelingResults_workspaceEntryId
            FOREIGN KEY (workspaceEntryId) REFERENCES WorkspaceEntries (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        MODIFY measurementContextId INT DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE ModelingResults
        DROP CONSTRAINT ModelingResults_workspaceEntryId,
        DROP workspaceEntryId
    """
    conn.execute(sql.text(query))

    # Clear out records with null measurementContextId, so we can set it to non-nullable
    query = "DELETE FROM ModelingResults WHERE measurementContextId IS NULL"
    conn.execute(sql.text(query))

    query = "ALTER TABLE ModelingResults MODIFY measurementContextId INT NOT NULL"
    conn.execute(sql.text(query))

if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
