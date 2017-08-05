import unittest

from exactly_lib.test_case_file_structure import path_relativity as sut
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType, \
    RelSdsOptionType


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestRelativityOptionTypeTranslations)


class TestRelativityOptionTypeTranslations(unittest.TestCase):
    def test_rel_any_from_rel_home(self):
        cases = [
            (RelHomeOptionType.REL_HOME, RelOptionType.REL_HOME),
        ]
        for rel_home_option, expected_rel_option in cases:
            with self.subTest(rel_home_option=str(rel_home_option)):
                actual = sut.rel_any_from_rel_home(rel_home_option)
                self.assertIs(expected_rel_option,
                              actual)

    def test_rel_any_from_rel_non_home(self):
        cases = [
            (RelNonHomeOptionType.REL_ACT, RelOptionType.REL_ACT),
            (RelNonHomeOptionType.REL_RESULT, RelOptionType.REL_RESULT),
            (RelNonHomeOptionType.REL_TMP, RelOptionType.REL_TMP),
            (RelNonHomeOptionType.REL_CWD, RelOptionType.REL_CWD),
        ]
        for rel_non_home_option, expected_rel_option in cases:
            with self.subTest(rel_non_home_option=str(rel_non_home_option)):
                actual = sut.rel_any_from_rel_non_home(rel_non_home_option)
                self.assertIs(expected_rel_option,
                              actual)

    def test_rel_any_from_rel_sds(self):
        cases = [
            (RelSdsOptionType.REL_ACT, RelOptionType.REL_ACT),
            (RelSdsOptionType.REL_RESULT, RelOptionType.REL_RESULT),
            (RelSdsOptionType.REL_TMP, RelOptionType.REL_TMP),
        ]
        for rel_sds_option, expected_rel_option in cases:
            with self.subTest(rel_sds_option=str(rel_sds_option)):
                actual = sut.rel_any_from_rel_sds(rel_sds_option)
                self.assertIs(expected_rel_option,
                              actual)

    def test_rel_non_home_from_rel_sds(self):
        cases = [
            (RelSdsOptionType.REL_ACT, RelNonHomeOptionType.REL_ACT),
            (RelSdsOptionType.REL_RESULT, RelNonHomeOptionType.REL_RESULT),
            (RelSdsOptionType.REL_TMP, RelNonHomeOptionType.REL_TMP),
        ]
        for rel_sds_option, expected_rel_option in cases:
            with self.subTest(rel_sds_option=str(rel_sds_option)):
                actual = sut.rel_non_home_from_rel_sds(rel_sds_option)
                self.assertIs(expected_rel_option,
                              actual)
