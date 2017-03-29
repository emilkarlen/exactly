import unittest

import exactly_lib_test.value_definition.test_resources.path_relativity
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import path_relativity as sut


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
                exactly_lib_test.value_definition.test_resources.path_relativity.equals_path_relativity_variants(
                    variants).apply_without_message(self, variants)

    def test_not_equals__different__absolute(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        lv = PathRelativityVariants({RelOptionType.REL_ACT}, True)
        rv = PathRelativityVariants({RelOptionType.REL_ACT}, False)
        with put.assertRaises(TestException):
            sut.equals_path_relativity_variants(lv).apply_without_message(put, rv)

    def test_not_equals__different__option_sets(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        lv = PathRelativityVariants({RelOptionType.REL_HOME,
                                     RelOptionType.REL_RESULT}, False)
        rv = PathRelativityVariants({RelOptionType.REL_HOME,
                                     RelOptionType.REL_ACT}, False)
        with put.assertRaises(TestException):
            sut.equals_path_relativity_variants(lv).apply_without_message(put, rv)
