from uuid import uuid4

import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Users
        ADD apiKey VARCHAR(100) DEFAULT NULL,
        ADD UNIQUE INDEX Users_apiKey (apiKey)
    """
    conn.execute(sql.text(query))

    for user_id, in conn.execute(sql.text("SELECT id from Users;")):
        query = """
            UPDATE Users
            SET apiKey = :api_key
            WHERE Users.id = :user_id
        """
        conn.execute(sql.text(query), {'api_key': str(uuid4()), 'user_id': user_id})


def down(conn):
    query = """
        ALTER TABLE Users
        DROP INDEX Users_apiKey,
        DROP apiKey
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
