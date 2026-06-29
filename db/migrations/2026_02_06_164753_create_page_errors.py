import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE PageErrors (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            fullPath TEXT NOT NULL,
            uuid varchar(36) DEFAULT NULL,
            userId int DEFAULT NULL,
            traceback TEXT NOT NULL,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE PageErrors;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
