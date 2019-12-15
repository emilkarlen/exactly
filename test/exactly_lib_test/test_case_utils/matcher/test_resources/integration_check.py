import unittest
from typing import Optional, Sequence, TypeVar, Generic, Callable

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MatcherWTraceAndNegation, \
    MatcherWTrace
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.test_resources.arrangements import ActResultProducer, ActEnvironment
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, all_validations_passes
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import tcds_with_act_as_curr_dir, TcdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class Arrangement:
    def __init__(self,
                 symbols: Optional[SymbolTable] = None,
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 act_result: Optional[ActResultProducer] = None,
                 post_population_action: TcdsAction = TcdsAction(),
                 ):
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.hds_contents = hds_contents
        self.non_hds_contents = non_hds_contents
        self.tcds_contents = tcds_contents
        self.act_result = act_result
        self.post_population_action = post_population_action


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


def constant_model(model: MODEL) -> Callable[[Tcds], MODEL]:
    def ret_val(tcds: Tcds) -> MODEL:
        return model

    return ret_val


def check(put: unittest.TestCase,
          source: ParseSource,
          model_constructor: Callable[[Tcds], MODEL],
          parser: Parser[MatcherTypeSdv[MODEL]],
          arrangement: Arrangement,
          expected_logic_value_type: LogicValueType,
          expected_value_type: ValueType,
          expectation: Expectation):
    _Checker(put, source, model_constructor, parser, arrangement,
             expected_logic_value_type,
             expected_value_type,
             expectation).check()


def check_with_source_variants(put: unittest.TestCase,
                               arguments: Arguments,
                               model_constructor: Callable[[Tcds], MODEL],
                               parser: Parser[MatcherTypeSdv[MODEL]],
                               arrangement: Arrangement,
                               expected_logic_value_type: LogicValueType,
                               expected_value_type: ValueType,
                               expectation: Expectation):
    for source in equivalent_source_variants__with_source_check__for_expression_parser(
            put, arguments):
        check(put, source, model_constructor, parser, arrangement,
              expected_logic_value_type,
              expected_value_type,
              expectation)


class _CheckIsDoneException(Exception):
    pass


class _Checker(Generic[MODEL]):
    def __init__(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 model_constructor: Callable[[Tcds], MODEL],
                 parser: Parser[MatcherTypeSdv[MODEL]],
                 arrangement: Arrangement,
                 expected_logic_value_type: LogicValueType,
                 expected_value_type: ValueType,
                 expectation: Expectation):
        self.put = put
        self.source = source
        self.model_constructor = model_constructor
        self.parser = parser
        self.arrangement = arrangement
        self.expected_logic_value_type = expected_logic_value_type
        self.expected_value_type = expected_value_type
        self.expectation = expectation
        self.hds = None
        self.tcds = None

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

        matcher_ddv = self._resolve_ddv(matcher_sdv)

        structure_tree_of_ddv = matcher_ddv.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_ddv,
                                                      'sanity of structure of ddv')

        with tcds_with_act_as_curr_dir(
                # pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            self.arrangement.post_population_action.apply(path_resolving_environment)
            self.hds = path_resolving_environment.hds

            self._check_with_hds(matcher_ddv)

            self.tcds = path_resolving_environment.tcds

            self._produce_act_result()

            self._check_with_sds(matcher_ddv)

    def _produce_act_result(self):
        if self.arrangement.act_result:
            act_result = self.arrangement.act_result.apply(ActEnvironment(self.tcds))
            write_act_result(self.tcds.sds, act_result)

    def _check_with_hds(self, ddv: MatcherDdv[MODEL]):
        self._check_validation_pre_sds(ddv)

    def _check_with_sds(self, ddv: MatcherDdv[MODEL]):
        self._check_validation_post_sds(ddv)

        matcher = self._resolve_primitive_value(ddv)
        structure_tree_of_primitive = matcher.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_primitive,
                                                      'sanity of structure of primitive')

        structure_tree_of_ddv = ddv.structure().render()
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
        result = validator.validate_pre_sds_if_applicable(self.hds)

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
            model = self.model_constructor(self.tcds)
            main_result__trace = matcher.matches_w_trace(model)

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
