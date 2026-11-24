import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Compartments
        ADD mediumId INT,
        ADD KEY Compartment_mediumId (mediumId),
        ADD CONSTRAINT Compartment_mediumId
            FOREIGN KEY (mediumId)
            REFERENCES Media (id)
            ON DELETE CASCADE ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Compartments
        DROP CONSTRAINT Compartment_mediumId,
        DROP mediumId
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
