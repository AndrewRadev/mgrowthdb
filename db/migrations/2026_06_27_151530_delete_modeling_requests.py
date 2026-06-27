import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE ModelingResults
        DROP CONSTRAINT Calculations_calculationTechniqueId,
        DROP requestId;
    """
    conn.execute(sql.text(query))

    query = "DROP TABLE ModelingRequests;"
    conn.execute(sql.text(query))


def down(conn):
    query = """
        CREATE TABLE ModelingRequests (
            id int NOT NULL AUTO_INCREMENT,
            `type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            jobUuid varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
            state varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            `error` text,
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            studyId varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (id),
            KEY ModelingRequests_studyId (studyId),
            CONSTRAINT ModelingRequests_studyId FOREIGN KEY (studyId) REFERENCES Studies (publicId)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        ADD requestId INT DEFAULT NULL,
        ADD CONSTRAINT Calculations_calculationTechniqueId
            FOREIGN KEY (requestId)
            REFERENCES ModelingRequests (id)
            ON DELETE CASCADE ON UPDATE CASCADE
    """
    conn.execute(sql.text(query))

if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
