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
    get_json,
)

root_url = 'http://localhost:8081/api/v1'
# root_url = 'https://mgrowthdb.gbiomed.kuleuven.be/api/v1'

experiment_id_data = get_json(root_url, "study/SMGDB00000007")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]

experiment_pairs = {
    "bh1": "bhbt",
    "bh2": "bhri",
    "ri1": "bhri",
    "ri2": "btri",
    "bt1": "bhbt",
    "bt2": "btri",
}

short_names = {
    "Bacteroides thetaiotaomicron VPI-5482": "BT",
    "Roseburia intestinalis L1-82":          "RI",
    "Blautia hydrogenotrophica DSM 10507":   "BH",
}

for metric in ('auc', 'growthRate'):
    interactions = calculate_api_interactions(
        metric=metric,
        technique='fc',
        experiment_pairs=experiment_pairs,
        experiment_data=experiment_data,
    )

    # from scripts.interactions.functions import pp
    # pp(interactions)

    save_html_table(f"s07_{metric}.html", interactions, short_names)
    save_chart(f"s07_{metric}", interactions, short_names)
