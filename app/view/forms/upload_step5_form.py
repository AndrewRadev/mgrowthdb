from wtforms import (
    FieldList,
    FormField,
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    TextAreaField,
    URLField,
)
from wtforms.validators import DataRequired, ValidationError, Length

from app.view.forms.base_form import BaseForm


class ExperimentPerturbationForm(BaseForm):
    class Meta:
        csrf = False

    # Note: converted to seconds when creating perturbation
    startTime = IntegerField('startTime', validators=[DataRequired()])
    endTime   = IntegerField('endTime',   validators=[DataRequired()])

    description = TextAreaField('description', validators=[DataRequired()])

    removedCompartmentName = SelectField('removedCompartmentName', choices=[], validate_choice=False)
    addedCompartmentName   = SelectField('addedCompartmentName',   choices=[], validate_choice=False)
    oldCommunityName       = SelectField('oldCommunityName',       choices=[], validate_choice=False)
    newCommunityName       = SelectField('newCommunityName',       choices=[], validate_choice=False)


class UploadStep5Form(BaseForm):
    class Meta:
        csrf_time_limit = None

    class ExperimentForm(BaseForm):
        class Meta:
            csrf = False

        class BioreplicateForm(BaseForm):
            class Meta:
                csrf = False

            name         = StringField('name', validators=[DataRequired(), Length(max=100)])
            position     = StringField('position', validators=[Length(max=100)])
            biosampleUrl = URLField('biosampleUrl')

        publicId       = HiddenField('publicId')
        name           = StringField('name', validators=[DataRequired(), Length(max=100)])
        description    = TextAreaField('description', validators=[DataRequired()])
        timepointCount = IntegerField('timepointCount', validators=[DataRequired()])

        cultivationMode = SelectField('cultivationMode', choices=[
            ('batch',     "Batch"),
            ('fed-batch', "Fed-batch"),
            ('chemostat', "Chemostat"),
            ('other',     "Other"),
        ])

        communityName = SelectField(
            'communityName',
            validators=[DataRequired()],
            choices=[],
            validate_choice=False,
        )
        compartmentNames = SelectMultipleField(
            'compartmentNames',
            validators=[DataRequired()],
            choices=[],
            validate_choice=False,
        )

        # Create a local reference to the class for metaprogramming purposes
        PerturbationForm = ExperimentPerturbationForm

        bioreplicates = FieldList(FormField(BioreplicateForm))
        perturbations = FieldList(FormField(PerturbationForm))

        def validate_bioreplicates(self, field):
            names = [b['name'] for b in field.data]
            self._validate_uniqueness("name", "names are not unique", names)

            if len(names) == 0:
                raise ValidationError("at least one is required")

    timeUnits = SelectField('timeUnits', choices=[
        ('d', 'Days (d)'),
        ('h', 'Hours (h)'),
        ('m', 'Minutes (m)'),
        ('s', 'Seconds (s)'),
    ])
    experiments = FieldList(FormField(ExperimentForm))

    def validate_experiments(self, field):
        # Local validation:
        names = [e['name'] for e in field.data]

        try:
            self._validate_uniqueness("experiment_names", "names are not unique", names)
        except ValidationError as e:
            for field in self.experiments:
                if field.data['name'] in self._duplicated_attributes['experiment_names']:
                    field.form_errors.append('name: not unique')
            raise e

        # Global bioreplicate validation:
        names = [
            bioreplicate['name']
            for experiment in field.data
            for bioreplicate in experiment['bioreplicates']
        ]
        self._validate_uniqueness("bioreplicate_names", "bioreplicate names are not globally unique", names)

    def get_batch_form(self):
        return UploadStep5BatchForm()


class UploadStep5BatchForm(BaseForm):
    class Meta:
        csrf_time_limit = None

    treatmentLabels     = StringField('treatmentLabels')
    treatmentValues     = StringField('treatmentValues')
    nameTemplate        = StringField('nameTemplate', validators=[DataRequired(), Length(max=100)])
    descriptionTemplate = TextAreaField('descriptionTemplate', validators=[DataRequired()])
    bioreplicateCount   = IntegerField('bioreplicateCount', validators=[DataRequired()], default=1)

    cultivationMode = SelectField('cultivationMode', choices=[
        ('batch',     "Batch"),
        ('fed-batch', "Fed-batch"),
        ('chemostat', "Chemostat"),
        ('other',     "Other"),
    ])

    communityName = SelectField(
        'communityName',
        validators=[DataRequired()],
        choices=[],
        validate_choice=False,
    )
    compartmentNames = SelectMultipleField(
        'compartmentNames',
        validators=[DataRequired()],
        choices=[],
        validate_choice=False,
    )
    timepointCount = IntegerField('timepointCount', validators=[DataRequired()])

    # Create a local reference to the class for metaprogramming purposes
    PerturbationForm = ExperimentPerturbationForm

    perturbations = FieldList(FormField(PerturbationForm))

    def get_experiment_data(self):
        treatment_labels = self.data['treatmentLabels'].split(',')
        treatment_values = self.data['treatmentValues'].split(',')

        experiment_data = []

        for label in treatment_labels:
            label = label.strip()

            for value in treatment_values:
                value = value.strip()

                name = self.data['nameTemplate']
                name = name.replace('{treatmentLabel}', label)
                name = name.replace('{treatmentValue}', value)

                description = self.data['descriptionTemplate']
                description = description.replace('{treatmentLabel}', label)
                description = description.replace('{treatmentValue}', value)

                bioreplicate_data = []
                for i in range(1, self.data['bioreplicateCount'] + 1):
                    bioreplicate_data.append({
                        "name": f"{name}_{i}",
                        "position": "",
                        "biosampleUrl": ""
                    })

                experiment_data.append({
                    'name':             name,
                    'description':      description,
                    'communityName':    self.data['communityName'],
                    'cultivationMode':  self.data['cultivationMode'],
                    'compartmentNames': self.data['compartmentNames'],
                    'timepointCount':   self.data['timepointCount'],
                    'perturbations':    self.data['perturbations'],
                    'bioreplicates':    bioreplicate_data,
                })

        return experiment_data
