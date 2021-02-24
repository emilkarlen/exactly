import unittest
from typing import Optional

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.impls.types.path import parse_path, path_relativities
from exactly_lib.symbol.sdv_structure import ReferenceRestrictions
from exactly_lib.symbol.value_type import WithStrRenderingType, ValueType
from exactly_lib.type_val_deps.sym_ref import restrictions
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions, value_restrictions as vr
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions as r
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import FailureOfIndirectReference
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as sut
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restrictions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFailureOfIndirectReference),
        unittest.makeSuite(TestEqualsOrReferenceRestrictions),
        unittest.makeSuite(TestEqualsReferenceRestrictions),
        unittest.makeSuite(TestIsStringMadeUpOfJustStringsReferenceRestrictions),
    ])


class TestIsFailureOfIndirectReference(unittest.TestCase):
    def test_pass(self):
        cases = [
            NEA(
                'default behaviour',
                sut.is_failure__of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], _new_em('error message')),
            ),
            NEA(
                'default behaviour with non-empty list',
                sut.is_failure__of_indirect_reference(),
                FailureOfIndirectReference('symbol_name', [], _new_em('error message')),
            ),
            NEA(
                'name of symbol',
                sut.is_failure__of_indirect_reference(failing_symbol=asrt.equals('the-failing-symbol')),
                FailureOfIndirectReference('the-failing-symbol', [], _new_em('error message')),
            ),
            NEA(
                'error message',
                sut.is_failure__of_indirect_reference(
                    error_message=asrt_text_doc.is_string_for_test_that_equals('the error message')
                ),
                FailureOfIndirectReference('symbol_name', [], _new_em('the error message'),
                                           asrt_text_doc.new_single_string_text_for_test__optional('meaning')
                                           ),
            ),
            NEA(
                'meaning of failure',
                sut.is_failure__of_indirect_reference(
                    meaning_of_failure=asrt_text_doc.is_string_for_test_that_equals('meaning')
                ),
                FailureOfIndirectReference('symbol_name', [], _new_em('the error message'),
                                           asrt_text_doc.new_single_string_text_for_test__optional('meaning'),
                                           ),
            ),
            NEA(
                'path to failing symbol',
                sut.is_failure__of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
                FailureOfIndirectReference('symbol_name', ['sym1', 'sym2'],
                                           _new_em('the error message')),
            ),
        ]
        for case in cases:
            with self.subTest(msg=case.name):
                case.expected.apply_without_message(self, case.actual)

    def test__default_behaviour__fail_if_symbol_name_is_not_string(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(),
            FailureOfIndirectReference(['this is a list - not a string'],
                                       [],
                                       _new_em('error message'))
        )

    def test__default_behaviour__fail_if_path_to_failing_symbol_is_not_a_list(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       'this is a string - not a list',
                                       _new_em('error message'))
        )

    def test__default_behaviour__fail_if_error_message_is_not_a_string(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       ErrorMessageWithFixTip(['this is a list - not a string'])),
        )

    def test__default_behaviour__fail_if_meaning_of_failure_has_invalid_type(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(),
            FailureOfIndirectReference(
                'failing_symbol',
                [],
                _new_em('error message'),
                meaning_of_failure='this is a string - not a TextResolver',
            )
        )

    def test_fail_if_symbol_name_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(failing_symbol=asrt.equals('expected_failing_symbol')),
            FailureOfIndirectReference('actual_failing_symbol',
                                       [],
                                       _new_em('error message'))
        )

    def test_fail_if_path_to_failing_symbol_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(path_to_failing_symbol=asrt.equals(['sym1', 'sym2'])),
            FailureOfIndirectReference('failing_symbol',
                                       ['sym1'],
                                       _new_em('error message'))
        )

    def test_fail_if_error_message_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(
                error_message=asrt_text_doc.is_string_for_test_that_equals('expected error message')
            ),
            FailureOfIndirectReference('failing_symbol',
                                       [],
                                       _new_em('actual error message'))
        )

    def test_fail_if_meaning_of_failure_is_unexpected(self):
        assert_that_assertion_fails(
            sut.is_failure__of_indirect_reference(
                error_message=asrt_text_doc.is_string_for_test_that_equals('expected meaning of failure')
            ),
            FailureOfIndirectReference(
                'failing_symbol',
                [],
                _new_em('error message'),
                meaning_of_failure=asrt_text_doc.new_single_string_text_for_test__optional('actual meaning of failure')
            )
        )


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
                    r.OrRestrictionPart(WithStrRenderingType.PATH, r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.ArbitraryValueWStrRenderingRestriction.of_any())),
                    r.OrRestrictionPart(
                        WithStrRenderingType.STRING,
                        r.ReferenceRestrictionsOnDirectAndIndirect(
                            vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING),
                            vr.ArbitraryValueWStrRenderingRestriction.of_any()))
                ]),
                r.OrReferenceRestrictions([
                    r.OrRestrictionPart(WithStrRenderingType.PATH, r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.ArbitraryValueWStrRenderingRestriction.of_any())),
                    r.OrRestrictionPart(
                        WithStrRenderingType.STRING,
                        r.ReferenceRestrictionsOnDirectAndIndirect(
                            vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING),
                            vr.ArbitraryValueWStrRenderingRestriction.of_any()))
                ]),
            ),
        ]
        for description, actual, expected in cases:
            assertion = sut.equals_reference_restrictions__or(expected)
            with self.subTest(msg=description):
                assertion.apply_without_message(self, actual)

    def test_fail__invalid_type(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            value_restrictions.is_string())
        self._assert_fails(expected, actual)

    def test_fail__different_number_of_sub_restrictions(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string())),
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        self._assert_fails(expected, actual)

    def test_fail__different_part_selector(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.PATH,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        self._assert_fails(expected, actual)

    def test_fail__different_part_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.ArbitraryValueWStrRenderingRestriction.of_any()))])
        self._assert_fails(expected, actual)

    @staticmethod
    def _assert_fails(expected: r.OrReferenceRestrictions, actual: ReferenceRestrictions):
        assertion = sut.equals_reference_restrictions__or(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        cases = [
            (
                sut.equals_reference_restrictions__w_str_rendering(
                    r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.ArbitraryValueWStrRenderingRestriction.of_any())
                ),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.ArbitraryValueWStrRenderingRestriction.of_any()),
            ),
            (
                sut.equals_reference_restrictions__w_str_rendering(
                    r.ReferenceRestrictionsOnDirectAndIndirect(
                        vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.LIST))
                ),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.LIST)),
            ),
            (
                sut.equals_reference_restrictions__w_str_rendering(r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING),
                    vr.ArbitraryValueWStrRenderingRestriction.of_any())),
                r.ReferenceRestrictionsOnDirectAndIndirect(
                    vr.ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING),
                    vr.ArbitraryValueWStrRenderingRestriction.of_any()),
            ),
            (
                sut.equals_reference_restrictions__w_str_rendering(
                    r.OrReferenceRestrictions([])),
                r.OrReferenceRestrictions([]),
            ),
        ]
        for assertion, actual in cases:
            with self.subTest(actual=actual):
                assertion.apply_without_message(self, actual)

    def test_fail__direct_and_indirect__different_node_restrictions(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            vr.ArbitraryValueWStrRenderingRestriction.of_any())
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            value_restrictions.is_string())
        self._fail(expected, actual)

    def test_fail__or__different_sub_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    vr.ArbitraryValueWStrRenderingRestriction.of_any()))
        ])
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))
        ])
        self._fail(expected, actual)

    def test_fail__or__direct_and_indirect(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))
        ])
        actual = r.ReferenceRestrictionsOnDirectAndIndirect(
            value_restrictions.is_string())
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__or(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            value_restrictions.is_string())
        actual = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))
        ])
        self._fail(expected, actual)

    def test_fail__direct_and_indirect__non_symbol_restriction(self):
        expected = r.ReferenceRestrictionsOnDirectAndIndirect(
            value_restrictions.is_string())
        actual = ValueTypeRestriction([ValueType.STRING])
        self._fail(expected, actual)

    def test_fail__or__non_symbol_restriction(self):
        expected = r.OrReferenceRestrictions([
            r.OrRestrictionPart(WithStrRenderingType.STRING,
                                r.ReferenceRestrictionsOnDirectAndIndirect(
                                    value_restrictions.is_string()))
        ])
        actual = ValueTypeRestriction([ValueType.STRING])
        self._fail(expected, actual)

    def _fail(self, expected: r.WithStrRenderingTypeRestrictions, actual: ReferenceRestrictions):
        assertion = sut.equals_reference_restrictions__w_str_rendering(expected)
        assert_that_assertion_fails(assertion, actual)


class TestIsStringMadeUpOfJustStringsReferenceRestrictions(unittest.TestCase):
    def test_pass(self):
        actual = reference_restrictions.is_string__all_indirect_refs_are_strings()
        assertion = sut.is_reference_restrictions__string__w_all_indirect_refs_are_strings()
        assertion.apply_without_message(self, actual)

    def test_fail(self):
        # ARRANGE #
        assertion = sut.is_reference_restrictions__string__w_all_indirect_refs_are_strings()

        cases = [
            NameAndValue(
                'is_any_type_w_str_rendering',
                reference_restrictions.is_any_type_w_str_rendering()
            ),
            NameAndValue(
                'ValueTypeRestriction / STRING',
                restrictions.ValueTypeRestriction.of_single(ValueType.STRING),
            ),
            NameAndValue(
                'ValueTypeRestriction / FILE_MATCHER',
                restrictions.ValueTypeRestriction.of_single(ValueType.FILE_MATCHER),
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
