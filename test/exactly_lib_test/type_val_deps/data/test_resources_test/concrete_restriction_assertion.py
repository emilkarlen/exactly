import unittest

from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import PathRelativityRestriction, \
    AnyDataTypeRestriction
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion as sut


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
