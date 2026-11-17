import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Media (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
            description TEXT DEFAULT NULL,
            mediadiveId VARCHAR(100) DEFAULT NULL,
            studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            KEY Media_studyId (studyId),
            CONSTRAINT Media_studyId
                FOREIGN KEY (studyId)
                REFERENCES Studies (publicId)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE MediumComponents (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            massConcentration float DEFAULT NULL,
            molarConcentration float DEFAULT NULL,
            mediadiveId INT DEFAULT NULL,
            mediumId INT NOT NULL,
            optional tinyint(1) NOT NULL DEFAULT '0',
            position INT NOT NULL DEFAULT 1,
            KEY MediumComponents_mediumId (mediumId),
            CONSTRAINT MediumComponents_mediumId
                FOREIGN KEY (mediumId)
                REFERENCES Media (id)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = "DROP TABLE MediumComponents;"
    conn.execute(sql.text(query))

    query = "DROP TABLE Media;"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
