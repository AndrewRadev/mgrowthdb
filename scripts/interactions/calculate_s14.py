import json
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

from scripts.interactions.functions import (
    get_json,
    calculate_api_interactions,
    pp,
    save_chart,
    save_html_table,
)

root_url = 'http://localhost:8081/api/v1'
# root_url = 'https://mgrowthdb.gbiomed.kuleuven.be/api/v1'

experiment_id_data = get_json(root_url, "study/SMGDB00000014")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]

for concentration in '0.1', '0.75':
    strain_associations = [
        (
            "Agrobacterium tumefaciens str. MWF001",
            "Agrobacterium tumefaciens str. MWF001 plate counts",
            [f"At_LA_{concentration}_mono", f"At_Ct_LA_{concentration}_co"],
        ),
        (
            "Comamonas testosteroni str. MWF001",
            "Comamonas testosteroni str. MWF001 plate counts",
            [f"Ct_LA_{concentration}_mono", f"At_Ct_LA_{concentration}_co"],
        ),
    ]

    interactions = calculate_api_interactions(
        metric='auc',
        experiment_data=experiment_data,
        strain_associations=strain_associations,
    )

    short_names = {
        "Agrobacterium tumefaciens str. MWF001": "At",
        "Comamonas testosteroni str. MWF001": "Ct",
    }

    save_html_table(f"s14_{concentration}.html", interactions, short_names)
    save_chart(f"s14_{concentration}", interactions, short_names)
