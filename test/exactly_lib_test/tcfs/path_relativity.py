import unittest

from exactly_lib.tcfs import path_relativity as sut
from exactly_lib.tcfs.path_relativity import RelHdsOptionType, RelOptionType, RelNonHdsOptionType, \
    RelSdsOptionType, DirectoryStructurePartition


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestRelativityOptionTypeTranslations),
        unittest.makeSuite(TestRelativityOptionTypeTranslationsToRelAny),
        unittest.makeSuite(TestDependencyDict),
        unittest.makeSuite(TestResolvingDependencyOf),
    ])


class TestRelativityOptionTypeTranslations(unittest.TestCase):
    def test_rel_any_from_rel_hds(self):
        cases = [
            (RelHdsOptionType.REL_HDS_CASE, RelOptionType.REL_HDS_CASE),
            (RelHdsOptionType.REL_HDS_ACT, RelOptionType.REL_HDS_ACT),
        ]
        for rel_hds_option, expected_rel_option in cases:
            with self.subTest(rel_hds_option=str(rel_hds_option)):
                actual = sut.rel_any_from_rel_hds(rel_hds_option)
                self.assertIs(expected_rel_option,
                              actual)

    def test_rel_any_from_rel_non_hds(self):
        cases = [
            (RelNonHdsOptionType.REL_ACT, RelOptionType.REL_ACT),
            (RelNonHdsOptionType.REL_RESULT, RelOptionType.REL_RESULT),
            (RelNonHdsOptionType.REL_TMP, RelOptionType.REL_TMP),
            (RelNonHdsOptionType.REL_CWD, RelOptionType.REL_CWD),
        ]
        for rel_non_hds_option, expected_rel_option in cases:
            with self.subTest(rel_non_hds_option=str(rel_non_hds_option)):
                actual = sut.rel_any_from_rel_non_hds(rel_non_hds_option)
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

    def test_rel_non_hds_from_rel_sds(self):
        cases = [
            (RelSdsOptionType.REL_ACT, RelNonHdsOptionType.REL_ACT),
            (RelSdsOptionType.REL_RESULT, RelNonHdsOptionType.REL_RESULT),
            (RelSdsOptionType.REL_TMP, RelNonHdsOptionType.REL_TMP),
        ]
        for rel_sds_option, expected_rel_option in cases:
            with self.subTest(rel_sds_option=str(rel_sds_option)):
                actual = sut.rel_non_hds_from_rel_sds(rel_sds_option)
                self.assertIs(expected_rel_option,
                              actual)


class TestRelativityOptionTypeTranslationsToRelAny(unittest.TestCase):
    # Depends on the translations tested above

    def test_rel_hds_from_rel_any__that_is_a__rel_hds(self):

        rel_hds_cases = [
            (RelHdsOptionType.REL_HDS_CASE, RelOptionType.REL_HDS_CASE),
            (RelHdsOptionType.REL_HDS_ACT, RelOptionType.REL_HDS_ACT),
        ]
        for rel_hds_option, rel_any_option in rel_hds_cases:
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_hds_from_rel_any(rel_any_option)
                self.assertIs(rel_hds_option,
                              actual)

    def test_rel_hds_from_rel_any__that_is_NOT_a__rel_hds(self):

        for rel_non_hds_option in RelNonHdsOptionType:
            rel_any_option = sut.rel_any_from_rel_non_hds(rel_non_hds_option)
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_hds_from_rel_any(rel_any_option)
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

        non_sds_options = [RelOptionType.REL_CWD] + [sut.rel_any_from_rel_hds(rh)
                                                     for rh in RelHdsOptionType]
        for rel_any_option in non_sds_options:
            with self.subTest(rel_any_option=str(rel_any_option)):
                actual = sut.rel_sds_from_rel_any(rel_any_option)
                self.assertIsNone(actual)


class TestDependencyDict(unittest.TestCase):
    def test_dependency_of_hds(self):
        expected = {RelOptionType.REL_HDS_CASE,
                    RelOptionType.REL_HDS_ACT}
        actual = sut.DEPENDENCY_DICT[DirectoryStructurePartition.HDS]
        self.assertEqual(expected,
                         actual)

    def test_dependency_of_non_hds(self):
        expected = {RelOptionType.REL_ACT,
                    RelOptionType.REL_TMP,
                    RelOptionType.REL_RESULT,
                    RelOptionType.REL_CWD}
        actual = sut.DEPENDENCY_DICT[DirectoryStructurePartition.NON_HDS]
        self.assertEqual(expected,
                         actual)


class TestResolvingDependencyOf(unittest.TestCase):
    def test(self):
        cases = [
            (RelOptionType.REL_HDS_CASE, DirectoryStructurePartition.HDS),
            (RelOptionType.REL_HDS_ACT, DirectoryStructurePartition.HDS),

            (RelOptionType.REL_ACT, DirectoryStructurePartition.NON_HDS),
            (RelOptionType.REL_RESULT, DirectoryStructurePartition.NON_HDS),
            (RelOptionType.REL_TMP, DirectoryStructurePartition.NON_HDS),
            (RelOptionType.REL_CWD, DirectoryStructurePartition.NON_HDS),
        ]
        for rel_option, expected_resolving_dependency in cases:
            with self.subTest(rel_option=str(rel_option)):
                actual = sut.RESOLVING_DEPENDENCY_OF[rel_option]
                self.assertIs(expected_resolving_dependency,
                              actual)
