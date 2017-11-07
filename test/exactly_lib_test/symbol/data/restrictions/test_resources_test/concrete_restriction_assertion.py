import unittest

from exactly_lib.symbol.data.restrictions import value_restrictions as vr, reference_restrictions as r
from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfIndirectReference
from exactly_lib.symbol.data.restrictions.value_restrictions import AnySymbolTypeRestriction, \
    StringRestriction, \
    FileRefRelativityRestriction
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.restriction import ReferenceRestrictions, TypeCategoryRestriction
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_system.value_type import DataValueType, TypeCategory
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFailureOfIndirectReference),
        unittest.makeSuite(TestIsNoRestriction),
        unittest.makeSuite(TestIsStringRestriction),
        unittest.makeSuite(TestEqualsStringRestriction),
        unittest.makeSuite(TestEqualsFileRefRelativityRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
        unittest.makeSuite(TestEqualsOrReferenceRestrictions),
        unittest.makeSuite(TestEqualsReferenceRestrictions),
    ])


class TestIsFailureOfIndirectReference(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                'default behaviour',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], ValueRestrictionFailure('error message')),
            ),
            (
                'default behaviour with non-empty list',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], ValueRestrictionFailure('error message')),
            ),
            (
                'name of symbol',
                sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('the-failing-symbol')),
                FailureOfIndirectReference('the-failing-symbol', [], ValueRestrictionFailure('error message')),
            ),
            (
                'error message',
                sut.is_failure_of_indirect_reference(error_message=asrt.equals('the error message')),
                FailureOfIndirectReference('symbol_name', [], ValueRestrictionFailure('the error message'),
                                           'meaning'),
            ),
            (
                'error message',
                sut.is_failure_of_indirect_reference(meaning_of_failure=asrt.equals('meaning')),
                FailureOfIndirectReference('symbol_name', [], ValueRestrictionFailure('the error message'),
                                           'meaning'),
            ),
            (
                'path to failing symbol',
                sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
                FailureOfIndirectReference('symbol_name', ['sym1', 'sym2'],
                                           ValueRestrictionFailure('the error message')),
            ),
        ]
        for description, assertion, actual in cases:
            with self.subTest(msg=description):
                assertion.apply_without_message(self, actual)

    def test__default_behaviour__fail_if_symbol_name_is_not_string(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference(['this is a list - not a string'],
                                       [],
                                       ValueRestrictionFailure('error message'))
        )

    def test__default_behaviour__fail_if_path_to_failing_symbol_is_not_a_list(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       'this is a string - not a list',
                                       ValueRestrictionFailure('error message'))
        )

    def test__default_behaviour__fail_if_error_message_is_not_a_string(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ValueRestrictionFailure(['this is a list - not a string'])),
        )

    def test__default_behaviour__fail_if_meaning_of_failure_is_not_a_string(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ValueRestrictionFailure('error message'),
                                       meaning_of_failure=['list - not a string'])
        )

    def test_fail_if_symbol_name_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('expected_failing_symbol')),
            FailureOfIndirectReference('actual_failing_symbol',
                                       [],
                                       ValueRestrictionFailure('error message'))
        )

    def test_fail_if_path_to_failing_symbol_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
            FailureOfIndirectReference('failing_symbol',
                                       ['sym1'],
                                       ValueRestrictionFailure('error message'))
        )

    def test_fail_if_error_message_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(error_message=asrt.equals('expected error message')),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ValueRestrictionFailure('actual error message'))
        )

    def test_fail_if_meaning_of_failure_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(error_message=asrt.equals('expected meaning of failure')),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ValueRestrictionFailure('error message'),
                                       meaning_of_failure='actual meaning of failure')
        )


class TestIsNoRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            AnySymbolTypeRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.is_any_data_type_restriction.apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        actual = StringRestriction()
        assert_that_assertion_fails(sut.is_any_data_type_restriction, actual)


class TestIsStringRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            StringRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.is_string_value_restriction.apply_without_message(self, restriction)

    def test_not_equals__different__types(self):
        actual = AnySymbolTypeRestriction()
        assert_that_assertion_fails(sut.is_string_value_restriction, actual)


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
        actual = AnySymbolTypeRestriction()
        assert_that_assertion_fails(sut.equals_string_restriction(expected), actual)


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
        assert_that_assertion_fails(sut.equals_file_ref_relativity_restriction(expected), actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME_CASE}, False))
        actual = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assert_that_assertion_fails(sut.equals_file_ref_relativity_restriction(expected), actual)


class TestEqualsValueRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            FileRefRelativityRestriction(PathRelativityVariants(set(), False)),
            FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, True)),
            StringRestriction(),
            AnySymbolTypeRestriction(),
        ]
        for restriction in test_cases:
            with self.subTest():
                sut.equals_value_restriction(restriction).apply_without_message(self, restriction)

    def test_not_equals__different__types__one_is_file_ref_relativity_variants(self):
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME_CASE}, False))
        actual = AnySymbolTypeRestriction()
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)

    def test_not_equals__different__types__one_is_string_restriction(self):
        expected = StringRestriction()
        actual = AnySymbolTypeRestriction()
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)

    def test_not_equals__same_type__different_accepted_relativity_variants(self):
        expected = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HOME_CASE}, False))
        actual = FileRefRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assert_that_assertion_fails(sut.equals_value_restriction(expected), actual)


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
                    r.OrRestrictionPart(DataValueType.PATH, r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.AnySymbolTypeRestriction())),
                    r.OrRestrictionPart(DataValueType.STRING,
                                        r.ReferenceRestrictionsOnDirectAndIndirect(
                                            vr.StringRestriction(),
                                            vr.AnySymbolTypeRestriction()))
                ]),
                r.OrReferenceRestrictions([
                    r.OrRestrictionPart(DataValueType.PATH, r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.AnySymbolTypeRestriction())),
                    r.OrRestrictionPart(DataValueType.STRING,
                                        r.ReferenceRestrictionsOnDirectAndIndirect(
                                            vr.StringRestriction(),
                                            vr.AnySymbolTypeRestriction()))
                ]),
            ),
        ]
        for description, actual, expected in cases:
            assertion = sut.equals_or_reference_restrictions(expected)
            with self.subTest(msg=description):
                assertion.apply_without_message(self, actual)

    def test_fail__invalid_type(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        self._assert_fails(expected, actual)

    def test_fail__different_number_of_sub_restrictions(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction())),
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        self._assert_fails(expected, actual)

    def test_fail__different_part_selector(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.PATH,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        self._assert_fails(expected, actual)

    def test_fail__different_part_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.AnySymbolTypeRestriction()))])
        self._assert_fails(expected, actual)

    @staticmethod
    def _assert_fails(expected: r.OrReferenceRestrictions, actual: ReferenceRestrictions):
        assertion = sut.equals_or_reference_restrictions(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                sut.equals_data_type_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.AnySymbolTypeRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.AnySymbolTypeRestriction()),
            ),
            (
                sut.equals_data_type_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.StringRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.StringRestriction()),
            ),
            (
                sut.equals_data_type_reference_restrictions(r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.StringRestriction(),
                    vr.AnySymbolTypeRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.StringRestriction(),
                    vr.AnySymbolTypeRestriction()),
            ),
            (
                sut.equals_data_type_reference_restrictions(r.OrReferenceRestrictions([])),
                r.OrReferenceRestrictions([]),
            ),
        ]
        for assertion, actual in cases:
            with self.subTest(actual=actual):
                assertion.apply_without_message(self, actual)

    def test_fail__direct_and_indirect__different_node_restrictions(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.AnySymbolTypeRestriction())
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        self._fail(expected, actual)

    def test_fail__or__different_sub_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.AnySymbolTypeRestriction()))
        ])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))
        ])
        self._fail(expected, actual)

    def test_fail__or__direct_and_indirect(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))
        ])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__or(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))
        ])
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__non_symbol_restriction(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        actual = TypeCategoryRestriction(TypeCategory.LOGIC)
        self._fail(expected, actual)

    def test_fail__or__non_symbol_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.StringRestriction()))
        ])
        actual = TypeCategoryRestriction(TypeCategory.LOGIC)
        self._fail(expected, actual)

    def _fail(self, expected: r.DataTypeReferenceRestrictions, actual: ReferenceRestrictions):
        assertion = sut.equals_data_type_reference_restrictions(expected)
        assert_that_assertion_fails(assertion, actual)
