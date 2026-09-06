import pandas as pd

from scripts.interactions.functions import (
    calculate_api_interactions,
    # save_html_table,
    # save_latex_table,
    save_chart,
    get_json,
    adjust_p_values,
)

# root_url = 'http://localhost:8081/api/v1'
root_url = 'https://mgrowthdb.gbiomed.kuleuven.be/api/v1'

short_names = {
    'Bacteroides cellulosilyticus CL02T12C19':     'B. cellulosilyticus',
    'Bacteroides finegoldii CL09T03C10':           'B. finegoldii',
    'Bacteroides fragilis CL03T12C07':             'B. fragilis',
    'Bacteroides ovatus 3_8_47FAA':                'B. ovatus',
    'Bacteroides thetaiotaomicron VPI-5482':       'B. thetaiotaomicron',
    'Bifidobacterium adolescentis ATCC 15703':     'B. adolescentis',
    'Blautia hydrogenotrophica DSM 10507':         'B. hydrogenotrophica',
    'Escherichia coli str. K-12 substr. MG1655':   'E. coli',
    'Flavonifractor plautii 1_3_50AFAA':           'F. plautii',
    'Lachnoclostridium clostridioforme 2_1_49FAA': 'L. clostridioforme',
    'Lachnoclostridium symbiosum WAL-14673':       'L. symbiosum',
    'Lactiplantibacillus plantarum ATCC 8014':     'L. plantarum',
    'Phocaeicola dorei 5_1_36/D4':                 'P. dorei',
    'Phocaeicola vulgatus ATCC 8482':              'P. vulgatus',
    'Roseburia intestinalis L1-82':                'R. intestinalis',
    'Ruminococcus gnavus CC55_001C':               'R. gnavus',
}

experiment_id_data = get_json(root_url, "study/SMGDB00000007")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]
experiment_pairs = [
    ("bh1", "bhbt"),
    ("bh2", "bhri"),
    ("ri1", "bhri"),
    ("ri2", "btri"),
    ("bt1", "bhbt"),
    ("bt2", "btri"),
]

s7_interactions = calculate_api_interactions(
    metric='auc',
    technique='fc',
    experiment_pairs=experiment_pairs,
    experiment_data=experiment_data,
)
for i in s7_interactions:
    i['study'] = 'SMGDB00000007'

experiment_id_data = get_json(root_url, "study/SMGDB00000008")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]
combined_culture = ("DeltaAll_1", "DeltaAll_2")
experiment_pairs = [
    ("DeltaEc",  combined_culture),
    ("DeltaLp",  combined_culture),
    ("DeltaBa",  combined_culture),
    ("DeltaBv",  combined_culture),
    ("DeltaBt",  combined_culture),
    ("DeltaBf",  combined_culture),
    ("DeltaBo",  combined_culture),
    ("DeltaBfr", combined_culture),
    ("DeltaBd",  combined_culture),
    ("DeltaLs",  combined_culture),
    ("DeltaLc",  combined_culture),
    ("DeltaBc",  combined_culture),
    ("DeltaFp",  combined_culture),
]

s8_interactions = calculate_api_interactions(
    metric='auc',
    technique='qpcr',
    experiment_pairs=experiment_pairs,
    experiment_data=experiment_data,
)
for i in s8_interactions:
    i['study'] = 'SMGDB00000008'

experiment_id_data = get_json(root_url, "study/SMGDB00000004")["experiments"]
experiment_data = [get_json(root_url, f"experiment/{e["id"]}") for e in experiment_id_data]
experiment_pairs = [
    ("RI", "RI_BH +Ac"),
    ("RI", "RI_FP"),
    ("FP", "FP_BH +Ac"),
    ("FP", "RI_FP"),
    ("BH", "RI_BH +Ac"),
    ("BH", "FP_BH +Ac"),
]

s4_interactions = calculate_api_interactions(
    metric='auc',
    technique='qpcr',
    experiment_pairs=experiment_pairs,
    experiment_data=experiment_data,
)
for i in s4_interactions:
    i['study'] = 'SMGDB00000004'

interactions = adjust_p_values(s4_interactions + s7_interactions + s8_interactions)

df = pd.DataFrame.from_dict(interactions)
df.to_csv("s04_s07_s08.csv", index=False)

# save_html_table("s04_s07_s08.html", interactions, short_names)
# save_latex_table("s04_s07_s08.latex", interactions, short_names)
save_chart("s04_s07_s08", interactions, short_names)
