import unittest

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction, NoRestriction, \
    StringRestriction, EitherStringOrFileRefRelativityRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.symbol.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsNoRestriction),
        unittest.makeSuite(TestIsStringRestriction),
        unittest.makeSuite(TestEqualsStringRestriction),
        unittest.makeSuite(TestEqualsFileRefRelativityRestriction),
        unittest.makeSuite(TestEqualsEitherStringOrFileRefRelativityRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
    ])


class TestIsNoRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            NoRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.is_no_restriction.apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        actual = StringRestriction()
        with put.assertRaises(TestException):
            sut.is_no_restriction.apply_without_message(put, actual)


class TestIsStringRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            StringRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.is_string_value_restriction.apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.is_string_value_restriction.apply_without_message(put, actual)


class TestEqualsStringRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            StringRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals_string_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = StringRestriction()
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.equals_string_restriction(expected).apply_without_message(put, actual)


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


class TestEqualsEitherStringOrFileRefRelativityRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            EitherStringOrFileRefRelativityRestriction(
                StringRestriction(),
                FileRefRelativityRestriction(PathRelativityVariants(set(), False))
            ),
            EitherStringOrFileRefRelativityRestriction(
                StringRestriction(),
                FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True))
            ),
        ]
        for restriction in test_cases:
            with self.subTest():
                assertion = sut.equals_either_string_or_file_ref_relativity_restriction(restriction)
                assertion.apply_without_message(self, restriction)

    def test_not_equals__different__file_ref_restriction(self):
        expected = EitherStringOrFileRefRelativityRestriction(
            StringRestriction(),
            FileRefRelativityRestriction(PathRelativityVariants(set(), False))
        )
        actual = EitherStringOrFileRefRelativityRestriction(
            StringRestriction(),
            FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True))
        )
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion = sut.equals_either_string_or_file_ref_relativity_restriction(expected)
            assertion.apply_without_message(put, actual)


class TestEqualsValueRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            FileRefRelativityRestriction(PathRelativityVariants(set(), False)),
            FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True)),
            StringRestriction(),
            NoRestriction(),
            EitherStringOrFileRefRelativityRestriction(
                StringRestriction(),
                FileRefRelativityRestriction(PathRelativityVariants(set(), False))),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals_value_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types__one_is_file_ref_relativity_variants(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME}, False))
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.equals_value_restriction(expected).apply_without_message(put, actual)

    def test_not_equals__different__types__one_is_string_restriction(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = StringRestriction()
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.equals_value_restriction(expected).apply_without_message(put, actual)

    def test_not_equals__different__types__one_is_either_string_or_file_ref_restriction(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = EitherStringOrFileRefRelativityRestriction(
            StringRestriction(),
            FileRefRelativityRestriction(PathRelativityVariants(set(), False)))
        actual = NoRestriction()
        with put.assertRaises(TestException):
            sut.equals_value_restriction(expected).apply_without_message(put, actual)

    def test_not_equals__same_type__different_accepted_relativity_variants(self):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME}, False))
        actual = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        with put.assertRaises(TestException):
            sut.equals_value_restriction(expected).apply_without_message(put, actual)
