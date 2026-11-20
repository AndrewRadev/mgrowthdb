import json
from pathlib import Path

from db import get_session
from app.model.orm import MediumIngredient

import sqlalchemy as sql
from long_task_printer import LongTask

base_dir_path        = Path('var/external_data/mediadive/')
ingredient_dump_path = base_dir_path / 'ingredient_dump.json'

with ingredient_dump_path.open() as f:
    ingredient_data = json.load(f)

long_task = LongTask(total_count=ingredient_data['count'])

data_to_insert = []

with get_session() as db_session:
    for entry in ingredient_data['data']:
        if entry['name'] == '':
            long_task.skip(1)
            continue

        with long_task.measure() as progress:
            existing_ingredient = db_session.scalars(
                sql.select(MediumIngredient)
                .where(MediumIngredient.mediadiveId == entry['id'])
            ).one_or_none()

            if existing_ingredient:
                print(f"[{progress}] Working on {existing_ingredient.name}: Update")

                existing_ingredient.name        = entry['name']
                existing_ingredient.mass        = entry['mass']
                existing_ingredient.chebiId     = entry['ChEBI']
                existing_ingredient.mediadiveId = entry['id']

                db_session.add(existing_ingredient)
                db_session.commit()
            else:
                print(f"[{progress}] Working on: {entry['name']}: Insert")
                # Accumulate taxa for a batch-insert
                data_to_insert.append({
                    'name':        entry['name'],
                    'mass':        entry['mass'],
                    'chebiId':     entry['ChEBI'],
                    'mediadiveId': entry['id'],
                })

    # Final insert of any leftovers after the loop:
    if len(data_to_insert) > 0:
        db_session.execute(sql.insert(MediumIngredient), data_to_insert)
        db_session.commit()
