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


experiment_id_data = get_json("study/SMGDB00000002")["experiments"]
experiment_data = [get_json(f"experiment/{e["id"]}") for e in experiment_id_data]

strain_associations = [
    (
        "Bacteroides thetaiotaomicron VPI-5482",
        "Bacteroides thetaiotaomicron VPI-5482 FC counts",
        ["BT_WC", "BTRI_WC"],
    ),
    (
        "Roseburia intestinalis L1-82",
        "Roseburia intestinalis L1-82 FC counts",
        ["RI_WC", "BTRI_WC"],
    ),
]

short_names = {
    "Bacteroides thetaiotaomicron VPI-5482": "BT",
    "Roseburia intestinalis L1-82": "RI",
}

interactions = calculate_api_interactions(
    metric='auc',
    experiment_data=experiment_data,
    strain_associations=strain_associations,
    short_names=short_names,
)

pp(sorted(interactions))
