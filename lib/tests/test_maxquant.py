import pandas as pd
from unittest import TestCase
from nose.tools import assert_equals
from .. import maxquant as module


class TestClean(TestCase):
    def test__remove_underscores(self):
        sequence = '_AEDSNTHR_'
        cleaned = module._clean(sequence)

        assert_equals('AEDSNTHR', cleaned)

    def test__replace_oxidation__with_mass_16(self):
        sequence = '_EQHPDM(ox)SVTK_'
        cleaned = module._clean(sequence)

        assert_equals('EQHPDM[+16]SVTK', cleaned)

    def test__append_mass_57_after_cystine(self):
        sequence = '_TKIEECVVCSDKK_'
        cleaned = module._clean(sequence)

        assert_equals('TKIEEC[+57]VVC[+57]SDKK', cleaned)

    def test__append_mass_14_after_acetylation(self):
        sequence = '_(ac)SGGA(ac)AEK_'
        cleaned = module._clean_acetylation(sequence)

        assert_equals('_S[+42]GGAA[+42]EK_', cleaned)

    def test__multiple_conditions(self):
        sequence = '_M(ox)RPG(ac)VACSVSQAQK_'
        cleaned = module._clean(sequence)

        assert_equals('M[+16]RPGV[+42]AC[+57]SVSQAQK', cleaned)


class TestDataframeManipulation(TestCase):
    def test__copy_and_insert_column_after(self):
        names = ['Luke', 'Han', 'Leia', 'Chewbacca']
        planets = ['Tattooine', 'Corellia', 'Alderaan', 'Kashyyyk']
        data_set = list(zip(names, planets))
        df = pd.DataFrame(data=data_set, columns=['Names', 'Planets'])

        module._copy_and_insert_column_after(df, 'Names', 'Surnames')

        assert_equals(
            df.columns.get_loc('Surnames'),
            df.columns.get_loc('Names') + 1)

        for (i, row) in df.iterrows():
            assert_equals(row.Names, row.Surnames)

    def test__clean_target_column(self):
        data_set = [
            '_AEDSNTHR_',
            '_(ac)SGGAAEK_',
            '_KCAEEAQLISSLK_',
            '_AHSIQIM(ox)K_']
        df = pd.DataFrame(data=data_set, columns=['Sequences'])

        module._clean_target_column(df, 'Sequences')

        expected = [
            'AEDSNTHR',
            'S[+42]GGAAEK',
            'KC[+57]AEEAQLISSLK',
            'AHSIQIM[+16]K']

        for (i, row) in df.iterrows():
            assert_equals(expected[i], row.Sequences)
