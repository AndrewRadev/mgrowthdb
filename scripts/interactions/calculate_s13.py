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

experiment_id_data = get_json(root_url, "study/SMGDB00000013")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]

strain_associations = [
    (
        "Agrobacterium tumefaciens str. MWF001",
        "Agrobacterium tumefaciens str. MWF001 plate counts",
        ["At", "At+Ct", "At+Oa", "At+Ms"],
    ),
    (
        "Comamonas testosteroni str. MWF001",
        "Comamonas testosteroni str. MWF001 plate counts",
        ["Ct", "At+Ct", "CtOa", "MsOa"],
    ),
    (
        "Microbacterium saperdae str. MWF001",
        "Microbacterium saperdae str. MWF001 plate counts",
        ["Ms", "At+Ms", "Ct+Ms", "MsOa"],
    ),
    (
        "Ochrobactrum anthropi str. MWF001",
        "Ochrobactrum anthropi str. MWF001 plate counts",
        ["Oa", "At+Oa", "CtOa", "MsOa"],
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
    "Microbacterium saperdae str. MWF001": "Ms",
    "Ochrobactrum anthropi str. MWF001": "Oa",
}

save_html_table("s13.html", interactions, short_names)
save_chart("s13.svg", interactions, short_names)
