import unittest

from exactly_lib.symbol.restrictions.value_restrictions import NoRestriction, FileRefRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.symbol.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsFileRefRelativityRestriction),
    ])


class TestEqualsFileRefRelativityRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathRelativityVariants(set(), False),
            PathRelativityVariants({RelOptionType.REL_ACT}, True),
        ]
        for variants in test_cases:
            restriction = FileRefRelativityRestriction(variants)
            with self.subTest():
                sut.equals_file_ref_relativity_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME}, False))
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.equals_file_ref_relativity_restriction(expected).apply_without_message(put, actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME}, False))
        actual = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        with put.assertRaises(TestException):
            sut.equals_file_ref_relativity_restriction(expected).apply_without_message(put, actual)
