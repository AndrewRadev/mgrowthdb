import tests.init  # noqa: F401

import unittest

from werkzeug.datastructures import ImmutableMultiDict

from tests.page_test import PageTest
from app.view.forms.upload_step5_form import UploadStep5BatchForm


class TestUploadStep5Form(PageTest):
    def test_batch_experiment_form(self):
        with self.app.app_context():
            form = UploadStep5BatchForm(ImmutableMultiDict({
                'treatmentLabels': 'Metronidazole, Eravacycline',
                'treatmentValues': '0.1, 0.2',
                'nameTemplate': 'EC+{treatmentValue}_{treatmentLabel}',
                'descriptionTemplate': 'E. coli with {treatmentValue}mg/L of {treatmentLabel}',
                'bioreplicateCount': '2',
                'cultivationMode': 'batch',
                'communityName': 'EC',
                'compartmentNames': 'WC',
                'timepointCount': '10',
            }))

            experiment_data = form.get_experiment_data()

            names = [e['name'] for e in experiment_data]
            self.assertEqual(names, [
                'EC+0.1_Metronidazole',
                'EC+0.2_Metronidazole',
                'EC+0.1_Eravacycline',
                'EC+0.2_Eravacycline',
            ])

            descriptions = [e['description'] for e in experiment_data]
            self.assertEqual(descriptions, [
                'E. coli with 0.1mg/L of Metronidazole',
                'E. coli with 0.2mg/L of Metronidazole',
                'E. coli with 0.1mg/L of Eravacycline',
                'E. coli with 0.2mg/L of Eravacycline',
            ])

            community_names = {e['communityName'] for e in experiment_data}
            self.assertEqual(community_names, {'EC'})

            bioreplicates = [b['name'] for e in experiment_data for b in e['bioreplicates']]
            self.assertEqual(bioreplicates, [
                'EC+0.1_Metronidazole_1',
                'EC+0.1_Metronidazole_2',
                'EC+0.2_Metronidazole_1',
                'EC+0.2_Metronidazole_2',
                'EC+0.1_Eravacycline_1',
                'EC+0.1_Eravacycline_2',
                'EC+0.2_Eravacycline_1',
                'EC+0.2_Eravacycline_2',
            ])

if __name__ == '__main__':
    unittest.main()
