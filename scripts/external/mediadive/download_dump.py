from pathlib import Path
from datetime import datetime, UTC

from long_task_printer import print_with_time

from app.model.lib.util import download_file

base_dir_path = Path('var/external_data/mediadive/')
base_dir_path.mkdir(exist_ok=True)

ingredient_dump_path = base_dir_path / 'ingredient_dump.json'

with print_with_time("Downloading MediaDive data dump"):
    ingredients_url = 'https://mediadive.dsmz.de/rest/ingredients'

    download_file(ingredients_url, ingredient_dump_path)

# Record time of this update:
with open('var/external_data/last_mediadive_update.txt', 'w') as f:
    f.write(datetime.now(UTC).isoformat())
