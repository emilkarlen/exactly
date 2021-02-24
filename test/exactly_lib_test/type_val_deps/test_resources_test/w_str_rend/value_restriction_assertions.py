import unittest

from exactly_lib.symbol.value_type import WithStrRenderingType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction, \
    ArbitraryValueWStrRenderingRestriction
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import ArrEx
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restriction_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsAnyValueRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
        unittest.makeSuite(TestEqualsPathRelativityRestriction),
    ])


class TestIsAnyValueRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            ArbitraryValueWStrRenderingRestriction.of_any(),
            ArbitraryValueWStrRenderingRestriction(tuple(WithStrRenderingType)),
        ]
        for restriction in test_cases:
            with self.subTest(restriction.accepted):
                sut.is__w_str_rendering().apply_without_message(
                    self, restriction)

    def test_not_equals__different_value_types(self):
        cases = [
            ArrEx(
                [WithStrRenderingType.STRING],
                [WithStrRenderingType.PATH],
            ),
            ArrEx(
                [WithStrRenderingType.LIST],
                [WithStrRenderingType.PATH],
            ),
            ArrEx(
                [WithStrRenderingType.LIST, WithStrRenderingType.PATH],
                [WithStrRenderingType.PATH],
            ),
            ArrEx(
                [WithStrRenderingType.PATH],
                [WithStrRenderingType.LIST, WithStrRenderingType.PATH],
            ),
        ]
        for case in cases:
            with self.subTest(actual=case.arrangement,
                              expected=case.expectation):
                expected = ArbitraryValueWStrRenderingRestriction(case.expectation)
                actual = ArbitraryValueWStrRenderingRestriction(case.arrangement)
                assert_that_assertion_fails(sut.equals(expected), actual)

    def test_not_equals__different__restriction_types(self):
        actual = ArbitraryValueWStrRenderingRestriction.of_any()
        assert_that_assertion_fails(
            sut.is__path_w_relativity(),
            actual,
        )


class TestEqualsValueRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathAndRelativityRestriction(PathRelativityVariants(set(), False)),
            PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True)),
            ArbitraryValueWStrRenderingRestriction.of_any(),
            ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING),
            ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.PATH),
            ArbitraryValueWStrRenderingRestriction([WithStrRenderingType.PATH, WithStrRenderingType.LIST]),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types__one_is_path_relativity_variants(self):
        expected = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = ArbitraryValueWStrRenderingRestriction.of_any()
        assert_that_assertion_fails(sut.equals(expected), actual)

    def test_not_equals__same_type__different_accepted_relativity_variants(self):
        expected = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assert_that_assertion_fails(sut.equals(expected), actual)


class TestEqualsPathRelativityRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathRelativityVariants(set(), False),
            PathRelativityVariants({RelOptionType.REL_ACT}, True),
        ]
        for variants in test_cases:
            restriction = PathAndRelativityRestriction(variants)
            with self.subTest():
                sut.equals__path_w_relativity(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        expected = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = ArbitraryValueWStrRenderingRestriction.of_any()
        assertion = sut.equals__path_w_relativity(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        expected = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = PathAndRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assertion = sut.equals__path_w_relativity(expected)
        assert_that_assertion_fails(assertion, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
