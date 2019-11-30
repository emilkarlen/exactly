import unittest
from typing import Optional, Sequence, TypeVar, Generic

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MatcherWTraceAndNegation, \
    MatcherWTrace
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, all_validations_passes
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class Arrangement:
    def __init__(self, symbols: Optional[SymbolTable] = None):
        self.symbols = symbol_table_from_none_or_value(symbols)


class Expectation:
    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            validation: ValidationExpectation = all_validations_passes(),
            main_result: ValueAssertion[MatchingResult] = asrt_matching_result.matches_value(True),
            is_hard_error: Optional[ValueAssertion[str]] = None,
    ):
        self.source = source
        self.symbol_references = symbol_references
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


is_pass = Expectation


def main_result_is_success() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def main_result_is_failure() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(False)


MODEL = TypeVar('MODEL')


def check(put: unittest.TestCase,
          source: ParseSource,
          model: MODEL,
          parser: Parser[MatcherTypeSdv[MODEL]],
          arrangement: Arrangement,
          expected_logic_value_type: LogicValueType,
          expected_value_type: ValueType,
          expectation: Expectation):
    _Checker(put, source, model, parser, arrangement,
             expected_logic_value_type,
             expected_value_type,
             expectation).check()


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model: MODEL,
                               parser: Parser[MatcherTypeSdv[MODEL]],
                               arrangement: Arrangement,
                               expected_logic_value_type: LogicValueType,
                               expected_value_type: ValueType,
                               expectation: Expectation):
    for source in equivalent_source_variants__with_source_check__for_expression_parser(
            put, arguments):
        check(put, source, model, parser, arrangement,
              expected_logic_value_type,
              expected_value_type,
              expectation)


class _CheckIsDoneException(Exception):
    pass


class _Checker(Generic[MODEL]):
    def __init__(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 model: MODEL,
                 parser: Parser[MatcherTypeSdv[MODEL]],
                 arrangement: Arrangement,
                 expected_logic_value_type: LogicValueType,
                 expected_value_type: ValueType,
                 expectation: Expectation):
        self.put = put
        self.source = source
        self.model = model
        self.parser = parser
        self.arrangement = arrangement
        self.expected_logic_value_type = expected_logic_value_type
        self.expected_value_type = expected_value_type
        self.expectation = expectation
        self.tcds = fake_tcds()

    def check(self):
        try:
            self._check()
        except _CheckIsDoneException:
            pass

    def _check(self):
        matcher_sdv = self._parse()

        self.expectation.symbol_references.apply_with_message(self.put,
                                                              matcher_sdv.references,
                                                              'reference')

        matcher_value = self._resolve_ddv(matcher_sdv)

        structure_tree_of_ddv = matcher_value.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_ddv,
                                                      'structure of ddv')

        self._check_validation_pre_sds(matcher_value)
        self._check_validation_post_sds(matcher_value)

        matcher = self._resolve_primitive_value(matcher_value)
        structure_tree_of_primitive = matcher.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_primitive,
                                                      'structure of primitive')

        structure_equals_ddv = asrt_d_tree.header_data_and_children_equal_as(structure_tree_of_ddv)
        structure_equals_ddv.apply_with_message(
            self.put,
            structure_tree_of_primitive,
            'structure of primitive should be same as that of ddv')

        self._check_application(matcher)

    def _parse(self) -> MatcherTypeSdv[MODEL]:
        sdv = self.parser.parse(self.source)
        asrt.is_instance(MatcherTypeSdv).apply_with_message(self.put,
                                                            sdv,
                                                            'SDV')
        assert isinstance(sdv, MatcherTypeSdv)

        self.put.assertIs(self.expected_logic_value_type,
                          sdv.logic_value_type,
                          'logic value type')
        self.put.assertIs(self.expected_value_type,
                          sdv.value_type,
                          'logic type')
        self.expectation.source.apply_with_message(self.put,
                                                   self.source,
                                                   'source after parse')

        return sdv

    def _resolve_ddv(self, matcher_sdv: MatcherTypeSdv[MODEL]) -> MatcherDdv[MODEL]:
        matcher_ddv = matcher_sdv.resolve(self.arrangement.symbols)

        asrt.is_instance(MatcherDdv).apply_with_message(self.put,
                                                        matcher_ddv,
                                                        'resolved ddv')

        assert isinstance(matcher_ddv, MatcherDdv)

        return matcher_ddv

    def _resolve_primitive_value(self, matcher_ddv: MatcherDdv[MODEL]) -> MatcherWTrace[MODEL]:
        ret_val = matcher_ddv.value_of_any_dependency(self.tcds)

        asrt.is_instance(MatcherWTrace).apply_with_message(self.put,
                                                           ret_val,
                                                           'primitive value')

        assert isinstance(ret_val, MatcherWTrace)

        return ret_val

    def _check_validation_pre_sds(self, matcher_ddv: MatcherDdv[MODEL]):
        validator = matcher_ddv.validator
        result = validator.validate_pre_sds_if_applicable(self.tcds.hds)

        self.expectation.validation.pre_sds.apply_with_message(self.put,
                                                               result,
                                                               'validation pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, matcher_ddv: MatcherDdv[MODEL]):
        validator = matcher_ddv.validator
        result = validator.validate_post_sds_if_applicable(self.tcds)

        self.expectation.validation.post_sds.apply_with_message(self.put,
                                                                result,
                                                                'validation post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_application(self, matcher: MatcherWTraceAndNegation[MODEL]):
        try:
            main_result__trace = matcher.matches_w_trace(self.model)

            self._check_application_result(main_result__trace)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_application_result(self,
                                  result: MatchingResult,
                                  ):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        self.expectation.main_result.apply_with_message(self.put,
                                                        result,
                                                        'main result')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is None:
            self.put.fail('Unexpected HARD_ERROR')
        else:
            assertion_on_text_renderer = asrt_text_doc.is_string_for_test(self.expectation.is_hard_error)
            assertion_on_text_renderer.apply_with_message(self.put, result.error,
                                                          'error message for hard error')
            raise _CheckIsDoneException()
