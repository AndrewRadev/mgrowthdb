import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE DemoProjects (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name varchar(100) NOT NULL,
            `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            description TEXT NOT NULL,
            position int NOT NULL default 0,
            showOnHomepage tinyint(1) DEFAULT '1',
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE DemoProjects;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
