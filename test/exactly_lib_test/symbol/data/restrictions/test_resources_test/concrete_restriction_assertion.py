import unittest
from typing import Optional

from exactly_lib.symbol import restriction
from exactly_lib.symbol.data.restrictions import value_restrictions as vr, reference_restrictions as r, \
    reference_restrictions
from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfIndirectReference
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction, \
    StringRestriction, \
    PathRelativityRestriction
from exactly_lib.symbol.data.value_restriction import ErrorMessageWithFixTip
from exactly_lib.symbol.restriction import TypeCategoryRestriction
from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.parse import parse_path, path_relativities
from exactly_lib.type_system.value_type import DataValueType, TypeCategory, ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFailureOfIndirectReference),
        unittest.makeSuite(TestIsNoRestriction),
        unittest.makeSuite(TestIsStringRestriction),
        unittest.makeSuite(TestEqualsStringRestriction),
        unittest.makeSuite(TestEqualsPathRelativityRestriction),
        unittest.makeSuite(TestEqualsValueRestriction),
        unittest.makeSuite(TestEqualsOrReferenceRestrictions),
        unittest.makeSuite(TestEqualsReferenceRestrictions),
        unittest.makeSuite(TestIsStringMadeUpOfJustStringsReferenceRestrictions),
    ])


class TestIsFailureOfIndirectReference(unittest.TestCase):
    def test_pass(self):
        cases = [
            NEA(
                'default behaviour',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], _new_em('error message')),
            ),
            NEA(
                'default behaviour with non-empty list',
                sut.is_failure_of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], _new_em('error message')),
            ),
            NEA(
                'name of symbol',
                sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('the-failing-symbol')),
                FailureOfIndirectReference('the-failing-symbol', [], _new_em('error message')),
            ),
            NEA(
                'error message',
                sut.is_failure_of_indirect_reference(
                    error_message=asrt_text_doc.is_string_for_test_that_equals('the error message')
                ),
                FailureOfIndirectReference('symbol_name', [], _new_em('the error message'),
                                           asrt_text_doc.new_single_string_text_for_test__optional('meaning')
                                           ),
            ),
            NEA(
                'meaning of failure',
                sut.is_failure_of_indirect_reference(
                    meaning_of_failure=asrt_text_doc.is_string_for_test_that_equals('meaning')
                ),
                FailureOfIndirectReference('symbol_name', [], _new_em('the error message'),
                                           asrt_text_doc.new_single_string_text_for_test__optional('meaning'),
                                           ),
            ),
            NEA(
                'path to failing symbol',
                sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
                FailureOfIndirectReference('symbol_name', ['sym1', 'sym2'],
                                           _new_em('the error message')),
            ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                case.expected.apply_without_message(self, case.actual)

    def test__default_behaviour__fail_if_symbol_name_is_not_string(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference(['this is a list - not a string'],
                                       [],
                                       _new_em('error message'))
        )

    def test__default_behaviour__fail_if_path_to_failing_symbol_is_not_a_list(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       'this is a string - not a list',
                                       _new_em('error message'))
        )

    def test__default_behaviour__fail_if_error_message_is_not_a_string(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ErrorMessageWithFixTip(['this is a list - not a string'])),
        )

    def test__default_behaviour__fail_if_meaning_of_failure_has_invalid_type(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(),
            FailureOfIndirectReference(
                'failing_symbol',
                [],
                _new_em('error message'),
                meaning_of_failure='this is a string - not a TextResolver',
            )
        )

    def test_fail_if_symbol_name_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(failing_symbol=asrt.equals('expected_failing_symbol')),
            FailureOfIndirectReference('actual_failing_symbol',
                                       [],
                                       _new_em('error message'))
        )

    def test_fail_if_path_to_failing_symbol_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
            FailureOfIndirectReference('failing_symbol',
                                       ['sym1'],
                                       _new_em('error message'))
        )

    def test_fail_if_error_message_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(
                error_message=asrt_text_doc.is_string_for_test_that_equals('expected error message')
            ),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       _new_em('actual error message'))
        )

    def test_fail_if_meaning_of_failure_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure_of_indirect_reference(
                error_message=asrt_text_doc.is_string_for_test_that_equals('expected meaning of failure')
            ),
            FailureOfIndirectReference(
                'failing_symbol',
                [],
                _new_em('error message'),
                meaning_of_failure=asrt_text_doc.new_single_string_text_for_test__optional('actual meaning of failure')
            )
        )


class TestIsNoRestriction(unittest.TestCase):
    def test_equals(self):
        test_cases = [
            AnyDataTypeRestriction(),
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
        actual = AnyDataTypeRestriction()
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
        actual = AnyDataTypeRestriction()
        assert_that_assertion_fails(sut.equals_string_restriction(expected), actual)


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
        assert_that_assertion_fails(sut.equals_path_relativity_restriction(expected), actual)

    def test_not_equals__different__accepted_relativity_variants(self):
        expected = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_HDS_CASE}, False))
        actual = PathRelativityRestriction(PathRelativityVariants({RelOptionType.REL_ACT}, False))
        assert_that_assertion_fails(sut.equals_path_relativity_restriction(expected), actual)


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
                        vr.AnyDataTypeRestriction())),
                    r.OrRestrictionPart(DataValueType.STRING,
                                        r.ReferenceRestrictionsOnDirectAndIndirect(
                                            vr.StringRestriction(),
                                            vr.AnyDataTypeRestriction()))
                ]),
                r.OrReferenceRestrictions([
                    r.OrRestrictionPart(DataValueType.PATH, r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.AnyDataTypeRestriction())),
                    r.OrRestrictionPart(DataValueType.STRING,
                                        r.ReferenceRestrictionsOnDirectAndIndirect(
                                            vr.StringRestriction(),
                                            vr.AnyDataTypeRestriction()))
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
                                    vr.AnyDataTypeRestriction()))])
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
                    vr.AnyDataTypeRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.AnyDataTypeRestriction()),
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
                    vr.AnyDataTypeRestriction())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.StringRestriction(),
                    vr.AnyDataTypeRestriction()),
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
            vr.AnyDataTypeRestriction())
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.StringRestriction())
        self._fail(expected, actual)

    def test_fail__or__different_sub_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(DataValueType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.AnyDataTypeRestriction()))
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


class TestIsStringMadeUpOfJustStringsReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        actual = reference_restrictions.string_made_up_by_just_strings()
        assertion = sut.is_string_made_up_of_just_strings_reference_restrictions()
        assertion.apply_without_message(self, actual)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_string_made_up_of_just_strings_reference_restrictions()

        cases = [
            NameAndValue(
                'is_any_data_type',
                reference_restrictions.is_any_data_type()
            ),
            NameAndValue(
                'ValueTypeRestriction / STRING',
                restriction.ValueTypeRestriction(ValueType.STRING),
            ),
            NameAndValue(
                'ValueTypeRestriction / FILE_MATCHER',
                restriction.ValueTypeRestriction(ValueType.FILE_MATCHER),
            ),
            NameAndValue(
                'path_or_string_reference_restrictions',
                parse_path.path_or_string_reference_restrictions(
                    path_relativities.ALL_REL_OPTION_VARIANTS
                ),
            ),
        ]

        for case in cases:
            with self.subTest(case.name):
                # ACT && ASSERT #

                assert_that_assertion_fails(assertion, case.value)


def _new_em(message: str,
            how_to_fix: Optional[str] = None) -> ErrorMessageWithFixTip:
    return ErrorMessageWithFixTip(
        asrt_text_doc.new_single_string_text_for_test(message),
        (
            None
            if how_to_fix is None
            else asrt_text_doc.new_single_string_text_for_test(how_to_fix)
        )
    )
