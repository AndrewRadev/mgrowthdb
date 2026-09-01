from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FormField, FieldList
from wtforms.validators import Optional


class SearchFormClause(FlaskForm):
    class Meta:
        csrf = False

    option = SelectField('option', choices=[
        'Study name',
        'Study ID',
        'Project name',
        'Project ID',
        'Experiment ID',
        'Microbial strain',
        'NCBI ID',
        'Metabolites',
        'chEBI ID',
    ])
    value = StringField('value', validators=[Optional()])
    logic_operator = SelectField('logic_operator', validators=[Optional()], choices=['AND', 'OR', 'NOT'])


class SearchForm(FlaskForm):
    clauses = FieldList(FormField(SearchFormClause), min_entries=1)
