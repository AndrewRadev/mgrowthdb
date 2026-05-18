import pandas as pd

from flask import (
    g,
    render_template,
    redirect,
    request,
)
from app.model.orm import WorkspaceEntry
from app.model.lib.chart import Chart
from app.model.lib.errors import LoginRequired
from app.view.forms.comparative_chart_form import ComparativeChartForm

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
    chart_form = ComparativeChartForm(g.db_session)
    errors = {}

    # TODO: user found by orcidId, check for public/private

    return render_template(
        "pages/workspaces/visualize.html",
        chart_form=chart_form,
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
