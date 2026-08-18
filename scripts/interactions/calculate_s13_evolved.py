import json
import requests
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

from scripts.interactions.functions import calculate_api_interactions, pp

root_url = 'http://localhost:8081/api/v1'
# root_url = 'https://mgrowthdb.gbiomed.kuleuven.be/api/v1'

def get_json(endpoint):
    response = requests.get(f"{root_url}/{endpoint}.json")
    response.raise_for_status()
    return response.json()


def get_df(endpoint):
    response = requests.get(f"{root_url}/{endpoint}.csv")
    response.raise_for_status()
    return pd.read_csv(BytesIO(response.content))


experiment_id_data = get_json("study/SMGDB00000013")["experiments"]
experiment_data = [get_json(f"experiment/{e["id"]}") for e in experiment_id_data]

strain_associations = [
    (
        "Agrobacterium tumefaciens str. MWF001",
        "Agrobacterium tumefaciens str. MWF001 plate counts",
        ["Evolved At", "Evolved AtCt"],
    ),
    (
        "Comamonas testosteroni str. MWF001",
        "Comamonas testosteroni str. MWF001 plate counts",
        ["Evolved Ct", "Evolved AtCt"],
    ),
]

short_names = {
    "Agrobacterium tumefaciens str. MWF001": "At",
    "Comamonas testosteroni str. MWF001": "Ct",
}

interactions = calculate_api_interactions(
    metric='auc',
    experiment_data=experiment_data,
    strain_associations=strain_associations,
    short_names=short_names,
)

pp(sorted(interactions))
