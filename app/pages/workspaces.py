import pandas as pd

from flask import (
    g,
    render_template,
    redirect,
    request,
)
from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired
from app.model.orm import WorkspaceEntry


# TODO (2026-05-15) Error if not logged in
def workspaces_index_page(orcidId):
    errors = {}

    if request.method == 'POST':
        file = request.files['data']

        new_entries = WorkspaceEntry.from_csv(
            file,
            g.current_user,
            include_error=request.form.get('includeError', False),
            metadata={
                'dataType':    request.form.get('dataType'),
                'subjectType': request.form.get('subjectType'),
                'units':       request.form.get('units'),
            }
        )
        g.db_session.add_all(new_entries)
        g.db_session.commit()

    return render_template(
        "pages/workspaces/index.html",
        errors=errors,
    )


def workspaces_visualize_page(orcidId):
    chart = Chart(time_units='h')
    errors = {}

    for axis in ('left', 'right'):
        for file in request.files.getlist(f"data-{axis}"):
            if file.filename == '':
                continue

            try:
                df = pd.read_csv(file)
            except pd.errors.EmptyDataError:
                errors[file.filename] = "No columns found in file"
                continue

            if len(df.columns) < 2:
                errors[file.filename] = f"Expected at least 2 columns, found {len(df.columns)}"
                continue

            c1 = df.columns[0]
            c2 = df.columns[1]
            if len(df.columns) > 2:
                c3 = df.columns[2]
            else:
                c3 = None

            label = f"<b>{file.filename}</b>: {c2}"
            units = request.form.get(f"units-{axis}")

            df.rename(columns={c1: "time", c2: "value", c3: "std"}, inplace=True)

            chart.add_df(df, units=units, label=label, axis=axis)

    return render_template(
        "pages/workspaces/visualize.html",
        chart=chart,
        errors=errors,
    )


def workspaces_data_preview_fragment():
    file = request.files['file']
    df = pd.read_csv(file)

    # TODO (2026-05-14) Error handling
    errors = []

    return render_template(
        "pages/workspaces/_data_preview.html",
        df=df,
        errors=errors,
    )
