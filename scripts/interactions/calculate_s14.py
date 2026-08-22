import json
import requests
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

from scripts.interactions.functions import (
    calculate_api_interactions,
    save_html_table,
    save_latex_table,
    save_chart,
    get_json,
)

root_url = 'http://localhost:8081/api/v1'
# root_url = 'https://mgrowthdb.gbiomed.kuleuven.be/api/v1'

experiment_id_data = get_json(root_url, "study/SMGDB00000014")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]

experiment_pairs = {
    "At_LA_0.1_mono":  "At_Ct_LA_0.1_co",
    "Ct_LA_0.1_mono":  "At_Ct_LA_0.1_co",
    "At_LA_0.75_mono": "At_Ct_LA_0.75_co",
    "Ct_LA_0.75_mono": "At_Ct_LA_0.75_co",
}

short_names = {
    "Agrobacterium tumefaciens str. MWF001": "At",
    "Comamonas testosteroni str. MWF001":    "Ct",
}

interactions = calculate_api_interactions(
    metric='auc',
    technique='plates',
    experiment_pairs=experiment_pairs,
    experiment_data=experiment_data,
)

from scripts.interactions.functions import pp
pp(interactions)

save_html_table("s14.html", interactions, short_names)
save_latex_table("s14.latex", interactions, short_names)
save_chart("s14", interactions, short_names)
