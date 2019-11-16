import unittest

from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction, \
    PathRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsPathRelativityRestriction),
    ])


class TestEqualsPathRelativityRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathRelativityVariants(set(), False),
            PathRelativityVariants({RelOptionType.REL_ACT}, True),
        ]
        for variants in test_cases:
            restriction = PathRelativityRestriction(variants)
            with self.subTest():
                sut.equals_path_relativity_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        expected = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = AnyDataTypeRestriction()
        assertion = sut.equals_path_relativity_restriction(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        expected = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assertion = sut.equals_path_relativity_restriction(expected)
        assert_that_assertion_fails(assertion, actual)
