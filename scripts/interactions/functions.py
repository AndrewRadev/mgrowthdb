import json

import numpy as np
from scipy.stats import ttest_ind, zscore


def pp(input):
    print(json.dumps(input, indent=2))


def calculate_api_interactions(metric, experiment_data, strain_associations, short_names):
    """
    Calculate interactions between the given strains from experiment data
    retrieved though the API

    :param metric: Either "growthRate" or "auc"
    :param experiment_data:
        Experimental metadata retrieved from the API that is to be filtered to
        find strain interactions. This does not include individual
        measurements, only metadata and aggregate metrics.
    :param strain_associations:
        List of tuples, each of which has the form:
        (<strain name>, <measurement label>, <list of experiment names>)
    :param short_names:
        A dictionary of strain names to their short names for visualization
        purposes.
    """
    assert(metric in ('growthRate', 'auc'))

    # Filter experiment data: for each experiment, pluck target measurements only, group by name
    # Identify mono and co-culture experiments

    strains, mono, pairs = _collect_cultures(metric, experiment_data, strain_associations)
    pairs = _calculate_ratios(strains, mono, pairs)

    _save_chart("tmp.dot", pairs, short_names)

    return pairs


def _collect_cultures(metric, experiment_data, strain_associations):
    pairs = {}
    mono = {}
    all_strains = set()

    for (strain, _, _) in strain_associations:
        all_strains.add(strain)
        mono[strain] = []

        for (other_strain, _, _) in strain_associations:
            if strain == other_strain:
                continue
            key = f"{strain} with {other_strain}"
            pairs[key] = []

    for (strain, measurement_label, experiment_names) in strain_associations:
        mono_measurements = []
        co_measurements = []

        for experiment in experiment_data:
            if experiment['name'] not in experiment_names:
                continue

            experiment_strain_names = {s['name'] for s in experiment['communityStrains']}
            experiment_strain_names = all_strains.intersection(experiment_strain_names)

            if len(experiment_strain_names) == 0:
                continue

            if len(experiment_strain_names) == 1:
                other_strain = None
            elif len(experiment_strain_names) == 2:
                other_strain = list(experiment_strain_names - {strain})[0]
            else:
                raise ValueError(f"Given experiment includes {len(strain_names)} strains")

            for bioreplicate in experiment['bioreplicates']:
                # Ignore computed bioreplicates
                if bioreplicate['isAverage']:
                    continue

                for measurement_context in bioreplicate['measurementContexts']:
                    # Only target the requested technique:
                    if measurement_context['label'] != measurement_label:
                        continue

                    value = measurement_context[metric]
                    print(measurement_label, f"{value:e}")

                    if other_strain:
                        pairs[f"{strain} with {other_strain}"].append(value)
                    else:
                        mono[strain].append(value)

    return all_strains, mono, pairs


def _calculate_ratios(strains, mono, pairs):
    ratios = []

    for strain in strains:
        for other_strain in strains:
            if strain == other_strain:
                continue

            pair_values = pairs[f"{strain} with {other_strain}"]
            mono_values = mono[strain]

            if len(pair_values) == 0:
                continue

            log_ratio = float(np.log10(np.mean(pair_values) / np.mean(mono_values)))
            p_value = ttest_ind(pair_values, mono_values).pvalue

            if p_value < 0.001:
                p_symbol = '***'
            elif p_value < 0.01:
                p_symbol = '**'
            elif p_value < 0.05:
                p_symbol = '*'
            else:
                p_symbol = ''

            ratios.append((strain, other_strain, log_ratio, p_value, p_symbol))

    return ratios


def _save_chart(filename, pairs, short_names):
    with open(filename, 'w') as f:
        print("""
            digraph G {
            graph [layout=dot rankdir=TD]
            node  [shape=box style=rounded]
        """, file=f)

        abs_log_ratios = [np.abs(log_ratio) for (_, _, log_ratio, _, _) in pairs]
        z_scores = zscore(abs_log_ratios)

        print(z_scores)

        for i, (first, second, log_ratio, p_value, p_symbol) in enumerate(pairs):
            if p_symbol == "":
                continue

            size = (z_scores[i] + 1.1) * 1.5

            if log_ratio > 0:
                color = "darkgreen"
            elif log_ratio <= 0:
                color = "brown"

            edge = ' -> '.join((short_names[second], short_names[first]))
            label = ', '.join((
                f"label=\"{p_symbol}\"",
                f"penwidth=\"{size}\"",
                f"color=\"{color}\"",
            ))

            print(f"{edge} [{label}]", file=f)

        print("}", file=f)
