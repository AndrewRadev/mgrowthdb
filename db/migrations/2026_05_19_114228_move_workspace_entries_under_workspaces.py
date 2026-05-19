import sqlalchemy as sql


def up(conn):
    # Add nullable workspaceId column first
    query = """
        ALTER TABLE WorkspaceEntries
        ADD workspaceId int DEFAULT NULL,
        ADD CONSTRAINT WorkspaceEntries_workspaceId FOREIGN KEY (workspaceId)
            REFERENCES Workspaces (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))

    # Iterate over users and create default workspaces:
    query = "SELECT id from Users;"
    for (user_id,) in conn.execute(sql.text(query)):
        # Create workspace:
        query = """
            INSERT INTO Workspaces (userId)
            VALUES (:user_id);
        """
        conn.execute(sql.text(query), {'user_id': user_id})
        (workspace_id,) = conn.execute(sql.text("SELECT LAST_INSERT_ID()")).one()

        # Assign workspace entries:
        query = """
            UPDATE WorkspaceEntries
            SET workspaceId = :workspace_id
            WHERE userId = :user_id
        """
        conn.execute(sql.text(query), {'workspace_id': workspace_id, 'user_id': user_id})

    # Make column not null:
    query = """
        ALTER TABLE WorkspaceEntries
        MODIFY workspaceId int NOT NULL
    """
    conn.execute(sql.text(query))

    # Remove now-useless user ids:
    query = "ALTER TABLE WorkspaceEntries DROP CONSTRAINT DashboardEntries_userId"
    conn.execute(sql.text(query))

    query = "ALTER TABLE WorkspaceEntries DROP userId"
    conn.execute(sql.text(query))


def down(conn):
    # Add nullable userId column first
    query = """
        ALTER TABLE WorkspaceEntries
        ADD userId int DEFAULT NULL,
        ADD CONSTRAINT DashboardEntries_userId FOREIGN KEY (userId)
            REFERENCES Users (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))

    # Iterate over deafult workspaces and assign userIds:
    query = """
        SELECT id, userId from Workspaces
        WHERE name = "default";
    """
    for (workspace_id, user_id) in conn.execute(sql.text(query)):
        # Assign workspace entries:
        query = """
            UPDATE WorkspaceEntries
            SET userId = :user_id
            WHERE workspaceId = :workspace_id
        """
        conn.execute(sql.text(query), {'workspace_id': workspace_id, 'user_id': user_id})

    # Make column not null:
    query = """
        ALTER TABLE WorkspaceEntries
        MODIFY userId int NOT NULL
    """
    conn.execute(sql.text(query))

    # Remove now-useless workspace ids and delete existing workspaces:
    query = "ALTER TABLE WorkspaceEntries DROP CONSTRAINT WorkspaceEntries_workspaceId"
    conn.execute(sql.text(query))

    query = "ALTER TABLE WorkspaceEntries DROP workspaceId"
    conn.execute(sql.text(query))

    query = "DELETE FROM Workspaces;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
