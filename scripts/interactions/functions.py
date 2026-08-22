import json
import subprocess
import requests
import itertools

import numpy as np
from scipy.stats import ttest_ind, zscore


def calculate_api_interactions(metric, technique, experiment_data, experiment_pairs):
    """
    Calculate interactions between the given strains from experiment data
    retrieved though the API

    :param metric: Either "growthRate" or "auc"
    :param technique: Type of the (strain-level) technique
    :param experiment_data:
        Experimental metadata retrieved from the API that is to be filtered to
        find strain interactions. This does not include individual
        measurements, only metadata and aggregate metrics.
    :param experiment_pairs:
        A dictionary indexed by the names of monocultures with values set to
        tuples of their respective co-cultures to use for interaction
        calculations.
    """
    assert metric in ('growthRate', 'auc')

    interactions = []

    experiments_by_name = {
        name: next(group)
        for name, group in itertools.groupby(experiment_data, lambda e: e['name'])
    }

    for mono_name, co_name in experiment_pairs.items():
        mono_exp = experiments_by_name[mono_name]
        co_exp   = experiments_by_name[co_name]

        mono_strains = [s['name'] for s in mono_exp['communityStrains']]
        co_strains   = [s['name'] for s in co_exp['communityStrains']]

        assert len(mono_strains) == 1
        assert len(co_strains) == 2

        focal_strain = mono_strains[0]
        assert focal_strain in co_strains

        other_strain = list(set(co_strains) - {focal_strain})[0]

        mono_values = _extract_measurements(metric, technique, focal_strain, mono_exp)
        co_values   = _extract_measurements(metric, technique, focal_strain, co_exp)

        log_ratio, p_value, p_symbol = _calculate_ratio(mono_values, co_values)

        interactions.append({
            'focal_strain': focal_strain,
            'other_strain': other_strain,
            'log_ratio':    log_ratio,
            'p_value':      p_value,
            'p_symbol':     p_symbol,
        })

    return interactions


def save_html_table(output_filename, interactions, short_names={}):
    with open(output_filename, 'w') as f:
        print("""
            <style>
              th, td {
                border: 1px solid black;
                padding: 6px;
              }
            </style>

            <table>
              <tr>
                <th>Focal strain</th>
                <th>Other strain</th>
                <th>Log ratio</th>
                <th>P-value</th>
                <th></th>
              </tr>
        """, file=f)

        sorted_interactions = sorted(interactions, key=lambda i: (i['focal_strain'], i['other_strain']))

        for interaction in sorted_interactions:
            focal_strain = interaction['focal_strain']
            other_strain = interaction['other_strain']

            print(f"""
                <tr>
                    <td>{short_names.get(focal_strain, focal_strain)}</td>
                    <td>{short_names.get(other_strain, other_strain)}</td>
                    <td>{interaction['log_ratio']:.5f}</td>
                    <td>{interaction['p_value']:.5f}</td>
                    <td>{interaction['p_symbol']}</td>
                </tr>
            """, file=f)

        print("""
            </table>
        """, file=f)


def save_latex_table(output_filename, interactions, short_names={}):
    with open(output_filename, 'w') as f:
        print(r"""
            \begin{tabular}{ ||l|l|r|r|l|| }
            \hline
            Focal strain & Other strain & Log-ratio & P-value & \\
            \hline
        """, file=f)

        sorted_interactions = sorted(interactions, key=lambda i: (i['focal_strain'], i['other_strain']))

        for interaction in sorted_interactions:
            focal_strain = interaction['focal_strain']
            other_strain = interaction['other_strain']

            print(' & '.join([
                short_names.get(focal_strain, focal_strain),
                short_names.get(other_strain, other_strain),
                f"{interaction['log_ratio']:.5f}",
                f"{interaction['p_value']:.3e}",
                interaction['p_symbol'],
            ]) + r'\\', file=f)

        print(r"""
            \hline
            \end{tabular}
        """, file=f)


def save_chart(output_prefix, interactions, short_names):
    with open(f"{output_prefix}.dot", 'w') as f:
        print("""
            digraph G {
            graph [layout=dot rankdir=TD]
            node  [shape=box style=rounded]
        """, file=f)

        abs_log_ratios = [np.abs(i['log_ratio']) for i in interactions]
        z_scores = zscore(abs_log_ratios)

        for i, interaction in enumerate(interactions):
            if interaction['p_symbol'] == "":
                continue

            size = (z_scores[i] + 1.1) * 1.5
            log_ratio = interaction['log_ratio']

            if log_ratio > 0:
                color = "darkgreen"
            elif log_ratio <= 0:
                color = "brown"

            focal_strain = interaction['focal_strain']
            other_strain = interaction['other_strain']

            first = short_names.get(focal_strain, focal_strain)
            second = short_names.get(other_strain, other_strain)

            edge = ' -> '.join((second, first))
            label = ', '.join((
                f"label=\"{interaction['p_symbol']}\"",
                f"penwidth=\"{size}\"",
                f"color=\"{color}\"",
            ))

            print(f"{edge} [{label}]", file=f)

        print("}", file=f)
        f.close()

        subprocess.run(['dot', '-Tsvg', f.name, f"-o{output_prefix}.svg"])


def get_json(root_url, endpoint):
    response = requests.get(f"{root_url}/{endpoint}.json")
    response.raise_for_status()
    return response.json()


def pp(input):
    print(json.dumps(input, indent=2))


def _extract_measurements(metric, technique, strain, experiment):
    measurements = []

    for bioreplicate in experiment['bioreplicates']:
        # Ignore computed bioreplicates
        if bioreplicate['isAverage']:
            continue

        for measurement_context in bioreplicate['measurementContexts']:
            # Only target the requested technique for strain measurements:
            if measurement_context['techniqueType'] != technique:
                continue

            # Only target the given strain measurements:
            if measurement_context['subject']['name'] != strain:
                continue

            measurement = measurement_context[metric]
            assert measurement is not None

            measurements.append(float(measurement))

    return measurements


def _calculate_ratio(mono_values, co_values):
    log_ratio = float(np.log10(np.mean(co_values) / np.mean(mono_values)))
    p_value = ttest_ind(co_values, mono_values).pvalue

    if p_value < 0.001:
        p_symbol = '***'
    elif p_value < 0.01:
        p_symbol = '**'
    elif p_value < 0.05:
        p_symbol = '*'
    else:
        p_symbol = ''

    return (log_ratio, p_value, p_symbol)
