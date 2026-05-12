import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE DashboardEntries (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            userId int NOT NULL,
            label VARCHAR(255) NOT NULL,
            data TEXT,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            KEY DashboardEntries_userId (userId)
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        DROP TABLE DashboardEntries;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
