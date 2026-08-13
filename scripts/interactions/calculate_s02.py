import json
import requests
from io import BytesIO

import numpy as np
import pandas as pd
from scipy.stats import ttest_ind

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


experiments = get_json("study/SMGDB00000002")["experiments"]

mono_bt_id = next(e["id"] for e in experiments if e['name'] == 'BT_WC')
mono_ri_id = next(e["id"] for e in experiments if e['name'] == 'RI_WC')
co_btri_id = next(e["id"] for e in experiments if e['name'] == 'BTRI_WC')

bt_mono = []
for bioreplicate in get_json(f"experiment/{mono_bt_id}")["bioreplicates"]:
    # Skip average bioreplicates, we want to only work with observational data:
    if bioreplicate['isAverage']:
        continue

    for mc in bioreplicate['measurementContexts']:
        if mc['subject']['name'].startswith('Bacteroides'):
            assert(mc['growthRate'] is not None)
            bt_mono.append(float(mc['growthRate']))

ri_mono = []
for bioreplicate in get_json(f"experiment/{mono_ri_id}")["bioreplicates"]:
    # Skip average bioreplicates, we want to only work with observational data:
    if bioreplicate['isAverage']:
        continue

    for mc in bioreplicate['measurementContexts']:
        if mc['subject']['name'].startswith('Roseburia'):
            assert(mc['growthRate'] is not None)
            ri_mono.append(float(mc['growthRate']))

bt_co = []
ri_co = []
for bioreplicate in get_json(f"experiment/{co_btri_id}")["bioreplicates"]:
    # Skip average bioreplicates, we want to only work with observational data:
    if bioreplicate['isAverage']:
        continue

    for mc in bioreplicate['measurementContexts']:
        if mc['subject']['name'].startswith('Bacteroides'):
            assert(mc['growthRate'] is not None)
            bt_co.append(float(mc['growthRate']))

        elif mc['subject']['name'].startswith('Roseburia'):
            assert(mc['growthRate'] is not None)
            ri_co.append(float(mc['growthRate']))

print(bt_mono)
print(bt_co)
print(ri_mono)
print(ri_co)

bt_log = np.log(np.mean(bt_co) / np.mean(bt_mono))
ri_log = np.log(np.mean(ri_co) / np.mean(ri_mono))

print("BT co:")
print(bt_co)
print("BT mono:")
print(bt_mono)
print(f"BT log-ratio: {bt_log}")
bt_t_test = ttest_ind(bt_co, bt_mono)
print(f"BT p-value: {bt_t_test.pvalue}")

print("RI co:")
print(ri_co)
print("RI mono:")
print(ri_mono)
print(f"RI log-ratio: {ri_log}")
ri_t_test = ttest_ind(ri_co, ri_mono)
print(f"RI p-value: {ri_t_test.pvalue}")
