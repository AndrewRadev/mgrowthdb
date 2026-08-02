import tempfile

from app.model.lib.r_script import RScript


def calculate_growth_rate(db_session, experiment, measurement_context):
    if experiment.cultivationMode != 'batch':
        return False

    if measurement_context.subjectType not in ('bioreplicate', 'strain'):
        return False

    if measurement_context.technique.type == 'ph':
        return False

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        data = measurement_context.get_df(db_session)
        # We don't need error columns for modeling:
        data = data[["time", "value"]]
        # Remove rows with NA values, if any
        data = data.dropna()

        if data.shape[0] < 6:
            return False

        try:
            rscript = RScript(root_path=tmp_dir_name)
            rscript.write_csv('input.csv', data)
            rscript.write_json('input.json', {'pointCount': 5})

            rscript.run('scripts/modeling/easy_linear.R')

            coefficients = rscript.read_key_value_json(
                'coefficients.json',
                key_name="_row",
                value_name="coefficients",
            )

            if coefficients is None:
                return False

            measurement_context.growthRate = coefficients['mumax']
            db_session.add(measurement_context)
            db_session.commit()

            return True
        except Exception as e:
            return False
