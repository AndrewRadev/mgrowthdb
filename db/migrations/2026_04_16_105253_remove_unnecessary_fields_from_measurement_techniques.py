import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        DROP CONSTRAINT MeasurementTechniques_studyId,
        DROP studyId,
        DROP units,
        DROP description;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MeasurementTechniques
        ADD description TEXT DEFAULT NULL,
        ADD units VARCHAR(100) DEFAULT NULL,
        ADD studyId VARCHAR(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD CONSTRAINT MeasurementTechniques_studyId
            FOREIGN KEY (studyId)
            REFERENCES Studies (publicId);
    """
    params = {}

    conn.execute(sql.text(query), params)


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
