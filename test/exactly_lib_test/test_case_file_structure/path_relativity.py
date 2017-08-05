import unittest

from exactly_lib.test_case_file_structure import path_relativity as sut
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType, \
    RelSdsOptionType, ResolvingDependency


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRelativityOptionTypeTranslations),
        unittest.makeSuite(TestDependencyDict),
        unittest.makeSuite(TestResolvingDependencyOf),
    ])


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


class TestDependencyDict(unittest.TestCase):
    def test_dependency_of_home(self):
        expected = {RelOptionType.REL_HOME}
        actual = sut.DEPENDENCY_DICT[ResolvingDependency.HOME]
        self.assertEqual(expected,
                         actual)

    def test_dependency_of_non_home(self):
        expected = {RelOptionType.REL_ACT,
                    RelOptionType.REL_TMP,
                    RelOptionType.REL_RESULT,
                    RelOptionType.REL_CWD}
        actual = sut.DEPENDENCY_DICT[ResolvingDependency.NON_HOME]
        self.assertEqual(expected,
                         actual)


class TestResolvingDependencyOf(unittest.TestCase):
    def test(self):
        cases = [
            (RelOptionType.REL_HOME, ResolvingDependency.HOME),

            (RelOptionType.REL_ACT, ResolvingDependency.NON_HOME),
            (RelOptionType.REL_RESULT, ResolvingDependency.NON_HOME),
            (RelOptionType.REL_TMP, ResolvingDependency.NON_HOME),
            (RelOptionType.REL_CWD, ResolvingDependency.NON_HOME),
        ]
        for rel_option, expected_resolving_dependency in cases:
            with self.subTest(rel_option=str(rel_option)):
                actual = sut.RESOLVING_DEPENDENCY_OF[rel_option]
                self.assertIs(expected_resolving_dependency,
                              actual)
