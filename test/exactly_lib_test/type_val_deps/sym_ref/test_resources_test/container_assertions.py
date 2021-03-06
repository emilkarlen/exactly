import unittest

from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.line_source import single_line_sequence
from exactly_lib_test.section_document.test_resources import source_location
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.sym_ref.test_resources import container_assertions as sut
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringSymbolValueContext
from exactly_lib_test.util.test_resources.line_source_assertions import equals_line_sequence


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestMatchesContainer)


class TestMatchesContainer(unittest.TestCase):
    def test_sdv_SHOULD_be_given_as_argument_to_sdv_assertion(self):
        # ARRANGE #
        actual_sdv = string_sdvs.str_constant('s')
        builtin_symbol = StringSymbolValueContext.of_sdv(actual_sdv, definition_source=None)
        assertion_that_is_expected_to_succeed = asrt.is_(actual_sdv)
        assertion_to_check = sut.matches_container(
            asrt.anything_goes(),
            assertion_that_is_expected_to_succeed,
            definition_source=asrt.anything_goes())
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, builtin_symbol.container)

    def test_source_line_SHOULD_be_given_as_argument_to_source_line_assertion(self):
        # ARRANGE #
        actual_sdv = string_sdvs.str_constant('s')
        source_line = single_line_sequence(1, 'source line')
        actual_container = StringSymbolValueContext(actual_sdv,
                                                    source_location.source_info_for_line_sequence(
                                                        source_line)).container
        assertion_that_is_expected_to_succeed = equals_line_sequence(source_line)
        assertion_to_check = sut.matches_container(
            value_type=asrt.anything_goes(),
            sdv=asrt.anything_goes(),
            definition_source=assertion_that_is_expected_to_succeed)
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_container)

    def test_failure_of_value_type(self):
        # ARRANGE #
        actual_container = StringSymbolValueContext.of_arbitrary_value().container
        assertion_to_check = sut.matches_container(
            value_type=asrt.is_(ValueType.PATH),
            sdv=asrt.anything_goes(),
            definition_source=asrt.anything_goes())
        assert_that_assertion_fails(assertion_to_check, actual_container)

    def test_arbitrary_failure(self):
        # ARRANGE #
        actual_sdv = string_sdvs.str_constant('s')
        source_line = single_line_sequence(1, 'source line')
        actual_container = StringSymbolValueContext(actual_sdv,
                                                    source_location.source_info_for_line_sequence(
                                                        source_line)).container
        assertion_that_is_expected_to_fail = asrt.not_(equals_line_sequence(source_line))
        assertion_to_check = sut.matches_container(
            value_type=asrt.anything_goes(),
            sdv=asrt.anything_goes(),
            definition_source=assertion_that_is_expected_to_fail)
        assert_that_assertion_fails(assertion_to_check, actual_container)
