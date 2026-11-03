import tempfile
import unittest
from pathlib import Path
import pandas as pd
from ml_harvest import REQUIRED, load_dataset


class HarvestDatasetTests(unittest.TestCase):
    def test_real_source_rejects_simulated_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'harvest.csv'
            row = {column: 'Riz' for column in REQUIRED}
            row.update({'pluviometrie_mm': 1200, 'engrais_kg_ha': 100, 'rendement_t_ha': 3.2, 'origine_donnees': 'simulées'})
            pd.DataFrame([row]).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, 'provenance simulée'):
                load_dataset(path, source='real')

    def test_real_excel_is_read_without_csv_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'harvest.xlsx'
            rows = []
            for i in range(100):
                row = {'culture':'Riz','region':'Poro','type_sol':'Argileux','type_semences':'Améliorée',
                       'irrigation':'Non','pratique_agricole':'Traditionnelle','pluviometrie_mm':1100+i,
                       'engrais_kg_ha':80+i,'rendement_t_ha':2.0+(i%7)/10}
                rows.append(row)
            pd.DataFrame(rows, columns=REQUIRED).to_excel(path, index=False)
            loaded = load_dataset(path, source='real')
            self.assertEqual(len(loaded), 100)


if __name__ == '__main__':
    unittest.main()
