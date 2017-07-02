import unittest

from exactly_lib.symbol import concrete_restrictions as r
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction, NoRestriction, \
    StringRestriction, EitherStringOrFileRefRelativityRestriction, FailureOfIndirectReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib_test.symbol.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFailureOfIndirectReference),
        unittest.makeSuite(TestIsNoRestriction),
        unittest.makeSuite(TestIsStringRestriction),
        unittest.makeSuite(TestEqualsStringRestriction),
        unittest.makeSuite(TestEqualsFileRefRelativityRestriction),
        unittest.makeSuite(TestEqualsEitherStringOrFileRefRelativityRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
        unittest.makeSuite(TestEqualsPathOrStringReferenceRestrictions),
        unittest.makeSuite(TestEqualsOrReferenceRestrictions),
        unittest.makeSuite(TestEqualsReferenceRestrictions),
    ])


class TestIsFailureOfIndirectReference(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                'default behaviour',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], 'error message'),
            ),
            (
                'default behaviour with non-empty list',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], 'error message'),
            ),
            (
                'name of symbol',
                sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('the-failing-symbol')),
                FailureOfIndirectReference('the-failing-symbol', [], 'error message'),
            ),
            (
                'error message',
                sut.is_failure_of_indirect_reference(error_message=asrt.equals('the error message')),
                FailureOfIndirectReference('symbol_name', [], 'the error message', 'meaning'),
            ),
            (
                'error message',
                sut.is_failure_of_indirect_reference(meaning_of_failure=asrt.equals('meaning')),
                FailureOfIndirectReference('symbol_name', [], 'the error message', 'meaning'),
            ),
            (
                'path to failing symbol',
                sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
                FailureOfIndirectReference('symbol_name', ['sym1', 'sym2'], 'the error message'),
            ),
        ]
        for description, assertion, actual in cases:
            with self.subTest(msg=description):
                assertion.apply_without_message(self, actual)

    def test__default_behaviour__fail_if_symbol_name_is_not_string(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference(['this is a list - not a string'],
                                       [],
                                       'error message')
        )

    def test__default_behaviour__fail_if_path_to_failing_symbol_is_not_a_list(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       'this is a string - not a list',
                                       'error message')
        )

    def test__default_behaviour__fail_if_error_message_is_not_a_string(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ['this is a list - not a string']),
        )

    def test__default_behaviour__fail_if_meaning_of_failure_is_not_a_string(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       'error message',
                                       meaning_of_failure=['list - not a string'])
        )

    def test_fail_if_symbol_name_is_unexpected(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('expected_failing_symbol')),
            FailureOfIndirectReference('actual_failing_symbol',
                                       [],
                                       'error message')
        )

    def test_fail_if_path_to_failing_symbol_is_unexpected(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
            FailureOfIndirectReference('failing_symbol',
                                       ['sym1'],
                                       'error message')
        )

    def test_fail_if_error_message_is_unexpected(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(error_message=asrt.equals('expected error message')),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       'actual error message')
        )

    def test_fail_if_meaning_of_failure_is_unexpected(self):
        self._assert_fails(
            sut.is_failure_of_indirect_reference(error_message=asrt.equals('expected meaning of failure')),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       'actual error message',
                                       meaning_of_failure='actual meaning of failure')
        )

    def _assert_fails(self,
                      assertion: asrt.ValueAssertion,
                      actual: FailureOfIndirectReference):
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            assertion.apply_without_message(put, actual)


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


class TestEqualsPathOrStringReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                PathRelativityVariants(set(), False),
                PathRelativityVariants(set(), False),
            ),
            (
                PathRelativityVariants(set(), True),
                PathRelativityVariants(set(), True),
            ),
            (
                PathRelativityVariants({RelOptionType.REL_TMP}, False),
                PathRelativityVariants({RelOptionType.REL_TMP}, False),
            ),
            (
                PathRelativityVariants({RelOptionType.REL_HOME, RelOptionType.REL_ACT}, True),
                PathRelativityVariants({RelOptionType.REL_HOME, RelOptionType.REL_ACT}, True),
            ),
        ]
        for expected_relativity_variants, actual_relativity_variants in cases:
            expected = r.PathOrStringReferenceRestrictions(expected_relativity_variants)
            actual = r.PathOrStringReferenceRestrictions(actual_relativity_variants)
            with self.subTest(actual=actual):
                assertion = sut.equals_path_or_string_reference_restrictions(expected)
                assertion.apply_without_message(self, actual)

    def test_fail_because_different_restriction_on_absolute(self):
        self._fail(PathRelativityVariants(set(), True),
                   PathRelativityVariants(set(), False))

    def test_fail_because_different_restriction_on_relativity__emptiness(self):
        self._fail(PathRelativityVariants({RelOptionType.REL_TMP}, False),
                   PathRelativityVariants(set(), False))

    def test_fail_because_different_restriction_on_relativity__relativity_option(self):
        self._fail(PathRelativityVariants({RelOptionType.REL_HOME}, False),
                   PathRelativityVariants({RelOptionType.REL_ACT}, False))

    def test_fail_because_different_restriction_on_relativity__number_of_relativity_options(self):
        self._fail(PathRelativityVariants({RelOptionType.REL_HOME}, False),
                   PathRelativityVariants({RelOptionType.REL_HOME, RelOptionType.REL_ACT}, False))

    def _fail(self,
              expected_relativity_variants: PathRelativityVariants,
              actual_relativity_variants: PathRelativityVariants):
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = r.PathOrStringReferenceRestrictions(expected_relativity_variants)
        actual = r.PathOrStringReferenceRestrictions(actual_relativity_variants)
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_path_or_string_reference_restrictions(expected)
            assertion.apply_without_message(put, actual)


class TestEqualsOrReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                'no parts',
                r.OrReferenceRestrictions([]),
                r.OrReferenceRestrictions([]),
            ),
            (
                'multiple parts',
                r.OrReferenceRestrictions([
                    r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction())),
                    r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(
                        r.StringRestriction(),
                        r.NoRestriction()))
                ]),
                r.OrReferenceRestrictions([
                    r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction())),
                    r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(
                        r.StringRestriction(),
                        r.NoRestriction()))
                ]),
            ),
        ]
        for description, actual, expected in cases:
            assertion = sut.equals_or_reference_restrictions(expected)
            with self.subTest(msg=description):
                assertion.apply_without_message(self, actual)

    def test_fail__invalid_type(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())
        self._assert_fails(expected, actual)

    def test_fail__different_number_of_sub_restrictions(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())),
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))])
        self._assert_fails(expected, actual)

    def test_fail__different_part(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()))])
        self._assert_fails(expected, actual)

    @staticmethod
    def _assert_fails(expected: r.OrReferenceRestrictions, actual: r.ReferenceRestrictions):
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_or_reference_restrictions(expected)
            assertion.apply_without_message(put, actual)


class TestEqualsReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                sut.equals_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()),
            ),
            (
                sut.equals_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()),
            ),
            (
                sut.equals_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction(),
                                                                                             r.NoRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction(),
                                                           r.NoRestriction()),
            ),
            (
                sut.equals_reference_restrictions(
                    r.PathOrStringReferenceRestrictions(
                        PathRelativityVariants({RelOptionType.REL_HOME}, False))),
                r.PathOrStringReferenceRestrictions(
                    PathRelativityVariants({RelOptionType.REL_HOME}, False)),
            ),
            (
                sut.equals_reference_restrictions(r.OrReferenceRestrictions([])),
                r.OrReferenceRestrictions([]),
            ),
        ]
        for assertion, actual in cases:
            with self.subTest(actual=actual):
                assertion.apply_without_message(self, actual)

    def test_fail__different_types__path_or_string(self):
        expected = r.PathOrStringReferenceRestrictions(
            PathRelativityVariants(set(), True))
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())
        self._fail(expected, actual)

    def test_fail__path_or_string(self):
        expected = r.PathOrStringReferenceRestrictions(PathRelativityVariants(set(), True))
        actual = r.PathOrStringReferenceRestrictions(PathRelativityVariants(set(), False))
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__different_node_restrictions(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction())
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())
        self._fail(expected, actual)

    def test_fail__or__different_sub_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.NoRestriction()))
        ])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))
        ])
        self._fail(expected, actual)

    def test_fail__or__direct_and_indirect(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))
        ])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__or(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction())
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(r.ReferenceRestrictionsOnDirectAndIndirect(r.StringRestriction()))
        ])
        self._fail(expected, actual)

    def _fail(self, expected: r.ReferenceRestrictions, actual: r.ReferenceRestrictions):
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_reference_restrictions(expected)
            assertion.apply_without_message(put, actual)
