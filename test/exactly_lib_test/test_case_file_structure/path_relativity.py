import unittest

from exactly_lib.test_case_file_structure import path_relativity as sut
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType, \
    RelSdsOptionType, DirectoryStructurePartition


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRelativityOptionTypeTranslations),
        unittest.makeSuite(TestRelativityOptionTypeTranslationsToRelAny),
        unittest.makeSuite(TestDependencyDict),
        unittest.makeSuite(TestResolvingDependencyOf),
    ])


class TestRelativityOptionTypeTranslations(unittest.TestCase):
    def test_rel_any_from_rel_home(self):
        cases = [
            (RelHomeOptionType.REL_HOME_CASE, RelOptionType.REL_HOME_CASE),
            (RelHomeOptionType.REL_HOME_ACT, RelOptionType.REL_HOME_ACT),
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


class TestRelativityOptionTypeTranslationsToRelAny(unittest.TestCase):
    # Depends on the translations tested above

    def test_rel_home_from_rel_any__that_is_a__rel_home(self):

        rel_home_cases = [
            (RelHomeOptionType.REL_HOME_CASE, RelOptionType.REL_HOME_CASE),
            (RelHomeOptionType.REL_HOME_ACT, RelOptionType.REL_HOME_ACT),
        ]
        for rel_home_option, rel_any_option in rel_home_cases:
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_home_from_rel_any(rel_any_option)
                self.assertIs(rel_home_option,
                              actual)

    def test_rel_home_from_rel_any__that_is_NOT_a__rel_home(self):

        for rel_non_home_option in RelNonHomeOptionType:
            rel_any_option = sut.rel_any_from_rel_non_home(rel_non_home_option)
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_home_from_rel_any(rel_any_option)
                self.assertIsNone(actual)

    def test_rel_sds_from_rel_any__that_is_a__rel_sds(self):

        rel_sds_cases = [
            (RelSdsOptionType.REL_ACT, RelOptionType.REL_ACT),
            (RelSdsOptionType.REL_RESULT, RelOptionType.REL_RESULT),
            (RelSdsOptionType.REL_TMP, RelOptionType.REL_TMP),
        ]

        for rel_sds_option, rel_any_option in rel_sds_cases:
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_sds_from_rel_any(rel_any_option)
                self.assertIs(rel_sds_option,
                              actual)

    def test_rel_sds_from_rel_any__that_is_NOT_a__rel_sds(self):

        non_sds_options = [RelOptionType.REL_CWD] + [sut.rel_any_from_rel_home(rh)
                                                     for rh in RelHomeOptionType]
        for rel_any_option in non_sds_options:
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_sds_from_rel_any(rel_any_option)
                self.assertIsNone(actual)


class TestDependencyDict(unittest.TestCase):
    def test_dependency_of_home(self):
        expected = {RelOptionType.REL_HOME_CASE,
                    RelOptionType.REL_HOME_ACT}
        actual = sut.DEPENDENCY_DICT[DirectoryStructurePartition.HOME]
        self.assertEqual(expected,
                         actual)

    def test_dependency_of_non_home(self):
        expected = {RelOptionType.REL_ACT,
                    RelOptionType.REL_TMP,
                    RelOptionType.REL_RESULT,
                    RelOptionType.REL_CWD}
        actual = sut.DEPENDENCY_DICT[DirectoryStructurePartition.NON_HOME]
        self.assertEqual(expected,
                         actual)


class TestResolvingDependencyOf(unittest.TestCase):
    def test(self):
        cases = [
            (RelOptionType.REL_HOME_CASE, DirectoryStructurePartition.HOME),
            (RelOptionType.REL_HOME_ACT, DirectoryStructurePartition.HOME),

            (RelOptionType.REL_ACT, DirectoryStructurePartition.NON_HOME),
            (RelOptionType.REL_RESULT, DirectoryStructurePartition.NON_HOME),
            (RelOptionType.REL_TMP, DirectoryStructurePartition.NON_HOME),
            (RelOptionType.REL_CWD, DirectoryStructurePartition.NON_HOME),
        ]
        for rel_option, expected_resolving_dependency in cases:
            with self.subTest(rel_option=str(rel_option)):
                actual = sut.RESOLVING_DEPENDENCY_OF[rel_option]
                self.assertIs(expected_resolving_dependency,
                              actual)
