import json
import requests
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

from scripts.interactions.functions import (
    calculate_api_interactions,
    save_html_table,
    save_chart,
    pp,
)

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


experiment_id_data = get_json("study/SMGDB00000007")["experiments"]
experiment_data = [get_json(f"experiment/{e["id"]}") for e in experiment_id_data]

# TODO (2026-08-20) Rewrite to just take experiment pairs and a list of strains

strain_associations = [
    (
        "Bacteroides thetaiotaomicron VPI-5482",
        "Bacteroides thetaiotaomicron VPI-5482 FC counts",
        ["bt1", "bt2", "bt3", "bhbt", "btri"],
    ),
    (
        "Blautia hydrogenotrophica DSM 10507",
        "Blautia hydrogenotrophica DSM 10507 FC counts",
        ["bh1", "bh2", "bh3", "bhbt", "bhri"],
    ),
    (
        "Roseburia intestinalis L1-82",
        "Roseburia intestinalis L1-82 FC counts",
        ["ri1", "ri2", "ri3", "bhri", "btri"],
    ),
]

short_names = {
    "Bacteroides thetaiotaomicron VPI-5482": "BT",
    "Roseburia intestinalis L1-82": "RI",
    "Blautia hydrogenotrophica DSM 10507": "BH",
}

interactions = calculate_api_interactions(
    metric='auc',
    experiment_data=experiment_data,
    strain_associations=strain_associations,
)

save_html_table(f"s07.html", interactions, short_names)
save_chart(f"s07", interactions, short_names)
