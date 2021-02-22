import unittest

from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import PathRelativityRestriction, \
    AnyDataTypeRestriction
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import StringRestriction
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.type_val_deps.test_resources.data import value_restriction, value_restriction as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsNoRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
        unittest.makeSuite(TestIsStringRestriction),
        unittest.makeSuite(TestEqualsStringRestriction),
        unittest.makeSuite(TestEqualsPathRelativityRestriction),
    ])


class TestIsNoRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            AnyDataTypeRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                value_restriction.is_value_restriction__convertible_to_string.apply_without_message(
                    self, restriction)

    def test_not_equals__different__types(self):
        actual = StringRestriction()
        assert_that_assertion_fails(
            value_restriction.is_value_restriction__convertible_to_string,
            actual)


class TestEqualsValueRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            PathRelativityRestriction(PathRelativityVariants(set(), False)),
            PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True)),
            StringRestriction(),
            AnyDataTypeRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals_value_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types__one_is_path_relativity_variants(self):
        expected = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = AnyDataTypeRestriction()
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)

    def test_not_equals__different__types__one_is_string_restriction(self):
        expected = StringRestriction()
        actual = AnyDataTypeRestriction()
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)

    def test_not_equals__same_type__different_accepted_relativity_variants(self):
        expected = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)


class TestIsStringRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            StringRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                value_restriction.is_value_restriction__string.apply_without_message(
                    self, restriction
                )

    def test_not_equals__different__types(self):
        actual = AnyDataTypeRestriction()
        assert_that_assertion_fails(
            value_restriction.is_value_restriction__string, actual
        )


class TestEqualsStringRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            StringRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals_string_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        expected = StringRestriction()
        actual = AnyDataTypeRestriction()
        assert_that_assertion_fails(
            sut.equals_string_restriction(expected), actual)


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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
