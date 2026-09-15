import os
import json
import csv
import itertools
import time
from pathlib import Path

import requests
import sqlalchemy as sql
from long_task_printer import LongTask

api_url = "https://api.ncbi.nlm.nih.gov/datasets/v2"

request_headers = {
    'Accept':       'application/json',
    'Content-Type': 'application/json',
}
if api_key := os.getenv('NCBI_API_KEY', None):
    request_headers['api-key'] = api_key

base_dir_path = Path('var/external_data/ncbi/')
input_path    = base_dir_path / 'data_dump_1.csv'
output_path   = base_dir_path / 'data_dump_2.csv'

# Count the number of lines in the file, should be quick:
with open(input_path) as f:
    ncbi_taxa_count = len(f.readlines())

# Create cache dir
(base_dir_path / 'cache').touch()

batch_size = 500
long_task = LongTask(total_count=ncbi_taxa_count // batch_size)

data = {}

with open(input_path) as r:
    reader = csv.DictReader(r)

    for i, row_batch in enumerate(itertools.batched(reader, batch_size)):
        ncbi_ids = [row['ncbiId'] for row in row_batch]

        cache_path = Path(base_dir_path / f"cache/json_{i:03}.json")

        if cache_path.exists():
            print(f"Skipping cached response: {i:03}.json")
            response_json = json.loads(cache_path.read_text())
            long_task.skip(1)
        else:
            with long_task.measure() as progress:
                print(f"[{progress}] Batch {i:03}")
                payload = json.dumps({"taxons": ncbi_ids})
                response = requests.post(
                    f'{api_url}/taxonomy/dataset_report',
                    data=payload,
                    headers={
                        'Accept':       'application/json',
                        'Content-Type': 'application/json',
                    }
                )
                response.raise_for_status()
                response_json = response.json()

                # Reduce the rate limiting:
                time.sleep(0.2)

                with open(cache_path, 'w') as cache:
                    json.dump(response_json, cache, indent=2)

        for report in response_json['reports']:
            if 'errors' in report:
                print(f"Skipping report due to errors: {report['errors']}")
                continue

            taxonomy = report['taxonomy']
            data[taxonomy['tax_id']] = {
                'name': taxonomy['current_scientific_name']['name'],
                'rank': taxonomy.get('rank', 'unknown').lower(),
                'genus': taxonomy['classification'].get('genus', {}).get('id', None),
                'species': taxonomy['classification'].get('species', {}).get('id', None),
            }

with open(output_path, 'w') as w:
    writer = csv.DictWriter(
        w,
        fieldnames=['ncbiId', 'name', 'rank', 'genusId', 'speciesId'],
        dialect='unix',
        quoting=csv.QUOTE_MINIMAL,
    )
    writer.writeheader()

    for ncbi_id, entry in data.items():
        writer.writerow({
            'ncbiId':    ncbi_id,
            'name':      entry['name'],
            'rank':      entry['rank'],
            'genusId':   entry['genus'],
            'speciesId': entry['species'],
        })
