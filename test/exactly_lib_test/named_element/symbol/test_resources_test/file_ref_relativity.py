import unittest

from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction, \
    FileRefRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.named_element.symbol.restrictions.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


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
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME_CASE}, False))
        actual = AnySymbolTypeRestriction()
        assertion = sut.equals_file_ref_relativity_restriction(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME_CASE}, False))
        actual = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assertion = sut.equals_file_ref_relativity_restriction(expected)
        assert_that_assertion_fails(assertion, actual)
