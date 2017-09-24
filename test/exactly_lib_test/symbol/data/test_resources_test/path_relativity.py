import unittest

import exactly_lib_test.symbol.data.test_resources.path_relativity
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.symbol.data.test_resources import path_relativity as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsPathRelativityVariants),
    ])


class TestEqualsPathRelativityVariants(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathRelativityVariants(set(), False),
            PathRelativityVariants({RelOptionType.REL_ACT}, True),
            PathRelativityVariants({RelOptionType.REL_ACT,
                                    RelOptionType.REL_RESULT}, False),
        ]
        for variants in test_cases:
            with self.subTest():
                exactly_lib_test.symbol.data.test_resources.path_relativity.equals_path_relativity_variants(
                    variants).apply_without_message(self, variants)

    def test_not_equals__different__absolute(self):
        lv = PathRelativityVariants({RelOptionType.REL_ACT}, True)
        rv = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        assertion = sut.equals_path_relativity_variants(lv)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, rv)

    def test_not_equals__different__option_sets(self):
        lv = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                     RelOptionType.REL_RESULT}, False)
        rv = PathRelativityVariants({RelOptionType.REL_HOME_CASE,
                                     RelOptionType.REL_ACT}, False)
        assertion = sut.equals_path_relativity_variants(lv)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, rv)
