import unittest
from contextlib import contextmanager
from typing import Optional, Sequence, TypeVar, Generic, Callable, ContextManager

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import MatcherTypeSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherDdv, MatcherWTraceAndNegation, \
    MatcherAdv, ApplicationEnvironment
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangement, \
    tcds_with_act_as_curr_dir_3
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources import assertions as asrt_matcher
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser, \
    equivalent_source_variants__with_source_check__for_expression_parser_2
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, all_validations_passes
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class Arrangement:
    def __init__(self,
                 symbols: Optional[SymbolTable] = None,
                 tcds: Optional[TcdsArrangement] = None,
                 ):
        """
        :param tcds: Not None iff TCDS is used (and must thus be created)
        """
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.tcds = tcds


def arrangement_w_tcds(tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                       hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                       non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                       act_result: Optional[ActResultProducer] = None,
                       pre_population_action: PlainTcdsAction = PlainTcdsAction(),
                       post_population_action: PlainTcdsAction = PlainTcdsAction(),
                       symbols: Optional[SymbolTable] = None,
                       ) -> Arrangement:
    """
    :return: An Arrangement with will create a TCDS
    """
    tcds = TcdsArrangement(
        hds_contents=hds_contents,
        non_hds_contents=non_hds_contents,
        tcds_contents=tcds_contents,
        act_result=act_result,
        pre_population_action=pre_population_action,
        post_population_action=post_population_action,
    )
    return Arrangement(symbols,
                       tcds)


def arrangement_wo_tcds(symbols: Optional[SymbolTable] = None) -> Arrangement:
    """
    :return: An Arrangement with will NOT create a TCDS
    """
    return Arrangement(symbols,
                       None)


class ParseExpectation:
    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
    ):
        self.source = source
        self.symbol_references = symbol_references


class ExecutionExpectation:
    def __init__(
            self,
            validation: ValidationAssertions = all_validations_passes(),
            main_result: ValueAssertion[MatchingResult] = asrt_matching_result.matches_value(True),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
    ):
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


class Expectation:
    def __init__(
            self,
            parse: ParseExpectation = ParseExpectation(),
            execution: ExecutionExpectation = ExecutionExpectation(),
    ):
        self.parse = parse
        self.execution = execution


is_pass = Expectation
EXECUTION_IS_PASS = ExecutionExpectation()


def main_result_is_success() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(True)


def main_result_is_failure() -> ValueAssertion[MatchingResult]:
    return asrt_matching_result.matches_value(False)


MODEL = TypeVar('MODEL')


def constant_model(model: MODEL) -> Callable[[FullResolvingEnvironment], MODEL]:
    def ret_val(environment: FullResolvingEnvironment) -> MODEL:
        return model

    return ret_val


class MatcherChecker(Generic[MODEL]):
    def __init__(self,
                 parser: Parser[MatcherTypeSdv[MODEL]],
                 expected_logic_value_type: LogicValueType,
                 ):
        self._parser = parser
        self._expected_logic_value_type = expected_logic_value_type

    @property
    def parser(self) -> Parser[MatcherTypeSdv[MODEL]]:
        return self._parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              model_constructor: Callable[[FullResolvingEnvironment], MODEL],
              arrangement: Arrangement,
              expectation: Expectation,
              ):
        checker = _ParseAndExecutionChecker(put,
                                            model_constructor,
                                            self._parser,
                                            arrangement,
                                            self._expected_logic_value_type,
                                            expectation)
        checker.check(source)

    def check__w_source_variants(self,
                                 put: unittest.TestCase, arguments: Arguments,
                                 model_constructor: Callable[[FullResolvingEnvironment], MODEL],
                                 arrangement: Arrangement,
                                 expectation: Expectation,
                                 ):
        for source in equivalent_source_variants__with_source_check__for_expression_parser(
                put, arguments):
            self.check(put, source, model_constructor, arrangement, expectation)

    def check_multi(self,
                    put: unittest.TestCase,
                    arguments: Arguments,
                    parse_expectation: ParseExpectation,
                    model_constructor: Callable[[FullResolvingEnvironment], MODEL],
                    execution: Sequence[NExArr[ExecutionExpectation, Arrangement]],
                    ):
        is_valid_sdv = asrt_matcher.matches_matcher_attributes(
            MatcherTypeSdv,
            self._expected_logic_value_type,
            parse_expectation.symbol_references
        )

        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        is_valid_sdv.apply_with_message(put, actual, 'parsed object')
        parse_expectation.source.apply_with_message(put, source, 'source after parse')

        for case in execution:
            with put.subTest(case.name):
                checker = _MatcherExecutionChecker(put, model_constructor, case.arrangement, case.expected)
                checker.check(actual)

    def check_multi__w_source_variants(self,
                                       put: unittest.TestCase,
                                       arguments: Arguments,
                                       symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                       model_constructor: Callable[[FullResolvingEnvironment], MODEL],
                                       execution: Sequence[NExArr[ExecutionExpectation, Arrangement]],
                                       ):
        is_valid_sdv = asrt_matcher.matches_matcher_attributes(
            MatcherTypeSdv,
            self._expected_logic_value_type,
            symbol_references
        )

        for source_case in equivalent_source_variants__with_source_check__for_expression_parser_2(arguments):
            with put.subTest(source_case.name):
                source = source_case.actual
                actual = self._parser.parse(source)
                is_valid_sdv.apply_with_message(put, actual, 'parsed object')
                source_case.expected.apply_with_message(put, source, 'source after parse')

                for case in execution:
                    with put.subTest(source_case=source_case.name,
                                     execution_case=case.name):
                        checker = _MatcherExecutionChecker(put, model_constructor, case.arrangement, case.expected)
                        checker.check(actual)

    def check_single_multi_execution_setup__for_test_of_test_resources(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            parse_expectation: ParseExpectation,
            model_constructor: Callable[[FullResolvingEnvironment], MODEL],
            execution: NExArr[ExecutionExpectation, Arrangement],
    ):
        is_valid_sdv = asrt_matcher.matches_matcher_attributes(
            MatcherTypeSdv,
            self._expected_logic_value_type,
            parse_expectation.symbol_references
        )

        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        is_valid_sdv.apply_with_message(put, actual, 'parsed object')
        parse_expectation.source.apply_with_message(put, source, 'source after parse')

        checker = _MatcherExecutionChecker(put, model_constructor, execution.arrangement, execution.expected)
        checker.check(actual)


class _CheckIsDoneException(Exception):
    pass


class _ParseAndExecutionChecker(Generic[MODEL]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: Callable[[FullResolvingEnvironment], MODEL],
                 parser: Parser[MatcherTypeSdv[MODEL]],
                 arrangement: Arrangement,
                 expected_logic_value_type: LogicValueType,
                 expectation: Expectation,
                 ):
        self.put = put
        self.parser = parser
        self.expected_logic_value_type = expected_logic_value_type
        self.expectation = expectation
        self._is_valid_sdv = asrt_matcher.matches_matcher_attributes(
            MatcherTypeSdv,
            self.expected_logic_value_type,
            self.expectation.parse.symbol_references
        )
        self.source_expectation = expectation.parse.source
        self._execution_checker = _MatcherExecutionChecker(put, model_constructor, arrangement, expectation.execution)

    def check(self, source: ParseSource):
        matcher_sdv = self._parse(source)
        self._execution_checker.check(matcher_sdv)

    def _parse(self, source: ParseSource) -> MatcherTypeSdv[MODEL]:
        sdv = self.parser.parse(source)
        self._is_valid_sdv.apply_with_message(self.put, sdv, 'parsed object')
        self.source_expectation.apply_with_message(self.put,
                                                   source,
                                                   'source after parse')
        return sdv


class _MatcherExecutionChecker(Generic[MODEL]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: Callable[[FullResolvingEnvironment], MODEL],
                 arrangement: Arrangement,
                 expectation: ExecutionExpectation,
                 ):
        self.put = put
        self.model_constructor = model_constructor
        self.arrangement = arrangement
        self.expectation = expectation
        self.hds = None
        self.tcds = None

    def check(self, sut: MatcherTypeSdv[MODEL]):
        try:
            self._check(sut)
        except _CheckIsDoneException:
            pass

    def _check(self, sut: MatcherTypeSdv[MODEL]):
        matcher_ddv = self._resolve_ddv(sut)

        structure_tree_of_ddv = matcher_ddv.structure().render()

        asrt_d_tree.matches_node().apply_with_message(self.put,
                                                      structure_tree_of_ddv,
                                                      'sanity of structure of ddv')

        with self._tcds_with_act_as_curr_dir() as tcds:
            self.hds = tcds.hds

            self._check_with_hds(matcher_ddv)

            self.tcds = tcds

            self._check_with_sds(matcher_ddv)

    def _tcds_with_act_as_curr_dir(self) -> ContextManager[Tcds]:
        tcds_arrangement = self.arrangement.tcds
        return (
            tcds_with_act_as_curr_dir_3(tcds_arrangement)
            if tcds_arrangement
            else
            self._dummy_tcds_setup()
        )

    @contextmanager
    def _dummy_tcds_setup(self) -> ContextManager[Tcds]:
        yield self.FAKE_TCDS

    def _check_with_hds(self, ddv: MatcherDdv[MODEL]):
        self._check_validation_pre_sds(ddv)

    def _check_with_sds(self, ddv: MatcherDdv[MODEL]):
        self._check_validation_post_sds(ddv)

        full_resolving_env = FullResolvingEnvironment(
            self.arrangement.symbols,
            self.tcds,
            ApplicationEnvironment(
                TmpDirFileSpaceAsDirCreatedOnDemand(self.tcds.sds.internal_tmp_dir / 'application-tmp-dir')
            ),
        )

        matcher = self._resolve_primitive_value(ddv, full_resolving_env.application_environment)
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

        self._check_application(matcher, full_resolving_env)

    def _resolve_ddv(self, matcher_sdv: MatcherTypeSdv[MODEL]) -> MatcherDdv[MODEL]:
        matcher_ddv = matcher_sdv.resolve(self.arrangement.symbols)

        asrt.is_instance(MatcherDdv).apply_with_message(self.put,
                                                        matcher_ddv,
                                                        'resolved ddv')

        assert isinstance(matcher_ddv, MatcherDdv)

        return matcher_ddv

    def _resolve_primitive_value(self,
                                 matcher_ddv: MatcherDdv[MODEL],
                                 application_environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        adv = matcher_ddv.value_of_any_dependency(self.tcds)

        asrt.is_instance(MatcherAdv).apply_with_message(self.put,
                                                        adv,
                                                        'adv')
        ret_val = adv.primitive(application_environment)

        asrt.is_instance(MatcherWTraceAndNegation).apply_with_message(self.put,
                                                                      ret_val,
                                                                      'primitive value')

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

    def _check_application(self,
                           matcher: MatcherWTraceAndNegation[MODEL],
                           resolving_env: FullResolvingEnvironment):
        try:
            model = self.model_constructor(resolving_env)
            main_result = matcher.matches_w_trace(model)

            self._check_application_result(main_result)
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
            self.expectation.is_hard_error.apply_with_message(self.put, result.error,
                                                              'error message for hard error')
            raise _CheckIsDoneException()


def _assert_is_valid_matcher_sdv(put: unittest.TestCase,
                                 expected_logic_value_type: LogicValueType,
                                 expected_value_type: ValueType,
                                 sdv):
    put.assertIsInstance(sdv, MatcherTypeSdv, 'SDV')
    assert isinstance(sdv, MatcherTypeSdv)
    put.assertIs(expected_logic_value_type,
                 sdv.logic_value_type,
                 'logic value type')
    put.assertIs(expected_value_type,
                 sdv.value_type,
                 'logic type')
