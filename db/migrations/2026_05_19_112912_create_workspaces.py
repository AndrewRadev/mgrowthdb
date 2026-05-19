import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Workspaces (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name varchar(100) NOT NULL DEFAULT "default",
            userId int NOT NULL,
            size int NOT NULL DEFAULT 0,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            publishedAt datetime DEFAULT NULL,
            UNIQUE INDEX Workspaces_userId_and_name (userId, name),
            CONSTRAINT Workspaces_userId FOREIGN KEY (userId)
                REFERENCES Users (id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE Workspaces;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
