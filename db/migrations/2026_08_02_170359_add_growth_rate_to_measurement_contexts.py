import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE MeasurementContexts
        ADD growthRate decimal(20,3) DEFAULT NULL
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE MeasurementContexts
        DROP growthRate
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
