import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE MediumIngredients (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            mass decimal(10,5) DEFAULT NULL,
            chebiId varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
            mediadiveId INT DEFAULT NULL,
            KEY MediumIngredients_name (name)
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE MediumIngredients;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
