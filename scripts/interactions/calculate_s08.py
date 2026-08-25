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

experiment_id_data = get_json(root_url, "study/SMGDB00000008")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]

combined_culture = ("DeltaAll_1", "DeltaAll_2")

experiment_pairs = {
    "DeltaEc":  combined_culture,
    "DeltaLp":  combined_culture,
    "DeltaBa":  combined_culture,
    "DeltaBv":  combined_culture,
    "DeltaBt":  combined_culture,
    "DeltaBf":  combined_culture,
    "DeltaBo":  combined_culture,
    "DeltaBfr": combined_culture,
    "DeltaBd":  combined_culture,
    "DeltaLs":  combined_culture,
    "DeltaLc":  combined_culture,
    "DeltaBc":  combined_culture,
    "DeltaFp":  combined_culture,
}

interactions = calculate_api_interactions(
    metric='auc',
    technique='qpcr',
    experiment_pairs=experiment_pairs,
    experiment_data=experiment_data,
)

save_html_table(f"s08.html", interactions)
save_latex_table(f"s08.latex", interactions)
save_chart(f"s08", interactions)
