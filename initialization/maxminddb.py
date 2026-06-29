from pathlib import Path

import maxminddb


def init_maxminddb(app):
    """
    Initialize the MaxmindDB database, if available. It maps IPs to countries,
    so we can count visitors by country.
    """
    maxminddb_path = Path('var/GeoLite2-Country.mmdb')

    if maxminddb_path.exists():
        try:
            setattr(app, 'maxminddb', maxminddb.open_database(maxminddb_path))
            # Note: this doesn't get a `close()` call, but we only read from
            # it, so it should be fine if the process gets killed.
        except maxminddb.InvalidDatabaseError:
            app.logger.warning(f"Maxmind DB exists, but can't be opened: {maxminddb_path}")
        except Exception as e:
            app.logger.warning(f"Error initializing maxminddb: {e}")

    return app
