import unittest
from contextlib import contextmanager
from typing import Optional, Sequence, Generic, Callable, ContextManager

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.logic_base_class import LogicDdv, ApplicationEnvironmentDependentValue, \
    ApplicationEnvironment
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import PlainTcdsAction
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import TcdsArrangement, \
    tcds_with_act_as_curr_dir_3
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.logic.test_resources.custom_properties_checker import \
    CustomPropertiesCheckerConfiguration, CustomExecutionPropertiesChecker, OUTPUT, APPLICATION_INPUT, PRIMITIVE
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser, \
    equivalent_source_variants__with_source_check__for_expression_parser_2
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, all_validations_passes
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


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


class ExecutionExpectation(Generic[OUTPUT]):
    def __init__(
            self,
            validation: ValidationAssertions = all_validations_passes(),
            main_result: ValueAssertion[OUTPUT] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
    ):
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error


class Expectation(Generic[OUTPUT]):
    def __init__(
            self,
            parse: ParseExpectation = ParseExpectation(),
            execution: ExecutionExpectation[OUTPUT] = ExecutionExpectation(),
    ):
        self.parse = parse
        self.execution = execution


EXECUTION_IS_PASS = ExecutionExpectation(
    main_result=asrt_matching_result.matches_value(True)
)


class IntegrationChecker(Generic[PRIMITIVE, APPLICATION_INPUT, OUTPUT]):
    def __init__(self,
                 parser: Parser[LogicSdv[PRIMITIVE]],
                 configuration: CustomPropertiesCheckerConfiguration[PRIMITIVE, APPLICATION_INPUT, OUTPUT],
                 ):
        self._parser = parser
        self._configuration = configuration

    @property
    def parser(self) -> Parser[LogicSdv[PRIMITIVE]]:
        return self._parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              model_constructor: APPLICATION_INPUT,
              arrangement: Arrangement,
              expectation: Expectation,
              ):
        checker = _ParseAndExecutionChecker(put,
                                            model_constructor,
                                            self._parser,
                                            arrangement,
                                            self._configuration,
                                            expectation)
        checker.check(source)

    def check__w_source_variants(self,
                                 put: unittest.TestCase, arguments: Arguments,
                                 model_constructor: APPLICATION_INPUT,
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
                    model_constructor: APPLICATION_INPUT,
                    execution: Sequence[NExArr[ExecutionExpectation, Arrangement]],
                    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')
        self._check_sdv(put, actual, parse_expectation.symbol_references)

        for case in execution:
            with put.subTest(case.name):
                checker = _IntegrationExecutionChecker(put,
                                                       model_constructor,
                                                       case.arrangement,
                                                       case.expected,
                                                       self._configuration.apply,
                                                       self._configuration.new_execution_checker(),
                                                       )
                checker.check(actual)

    def check_multi__w_source_variants(self,
                                       put: unittest.TestCase,
                                       arguments: Arguments,
                                       symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                       model_constructor: APPLICATION_INPUT,
                                       execution: Sequence[NExArr[ExecutionExpectation, Arrangement]],
                                       ):
        for source_case in equivalent_source_variants__with_source_check__for_expression_parser_2(arguments):
            with put.subTest(source_case.name):
                source = source_case.actual
                actual = self._parser.parse(source)
                source_case.expected.apply_with_message(put, source, 'source after parse')
                self._check_sdv(put, actual, symbol_references)

                for case in execution:
                    with put.subTest(source_case=source_case.name,
                                     execution_case=case.name):
                        checker = _IntegrationExecutionChecker(put,
                                                               model_constructor,
                                                               case.arrangement,
                                                               case.expected,
                                                               self._configuration.apply,
                                                               self._configuration.new_execution_checker(),
                                                               )
                        checker.check(actual)

    def check_single_multi_execution_setup__for_test_of_test_resources(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            parse_expectation: ParseExpectation,
            model_constructor: APPLICATION_INPUT,
            execution: NExArr[ExecutionExpectation, Arrangement],
    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')

        self._check_sdv(put, actual, parse_expectation.symbol_references)

        checker = _IntegrationExecutionChecker(put,
                                               model_constructor,
                                               execution.arrangement,
                                               execution.expected,
                                               self._configuration.apply,
                                               self._configuration.new_execution_checker(),
                                               )
        checker.check(actual)

    def _check_sdv(self,
                   put: unittest.TestCase,
                   parsed_object,
                   symbol_references: ValueAssertion[Sequence[SymbolReference]],
                   ):
        message_builder = asrt.MessageBuilder('parsed object')
        asrt.is_instance(LogicSdv).apply(put,
                                         parsed_object,
                                         message_builder.for_sub_component('object type'))

        assert isinstance(parsed_object, LogicSdv)  # Type info for IDE

        self._configuration.new_sdv_checker().check(put,
                                                    parsed_object,
                                                    message_builder)
        symbol_references.apply(put,
                                parsed_object.references,
                                message_builder.for_sub_component('symbol references'))


class _CheckIsDoneException(Exception):
    pass


class _ParseAndExecutionChecker(Generic[PRIMITIVE, APPLICATION_INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: APPLICATION_INPUT,
                 parser: Parser[LogicSdv[PRIMITIVE]],
                 arrangement: Arrangement,
                 configuration: CustomPropertiesCheckerConfiguration[PRIMITIVE, APPLICATION_INPUT, OUTPUT],
                 expectation: Expectation[OUTPUT],
                 ):
        self.put = put
        self.parser = parser
        self.configuration = configuration
        self.expectation = expectation
        self.source_expectation = expectation.parse.source
        self._execution_checker = _IntegrationExecutionChecker(put,
                                                               model_constructor,
                                                               arrangement,
                                                               expectation.execution,
                                                               configuration.apply,
                                                               configuration.new_execution_checker(),
                                                               )

    def check(self, source: ParseSource):
        matcher_sdv = self._parse(source)
        self._execution_checker.check(matcher_sdv)

    def _parse(self, source: ParseSource) -> LogicSdv[PRIMITIVE]:
        sdv = self.parser.parse(source)

        self.source_expectation.apply_with_message(
            self.put,
            source,
            'source after parse',
        )

        message_builder = asrt.MessageBuilder('parsed object')

        self.expectation.parse.symbol_references.apply(
            self.put,
            sdv.references,
            message_builder.for_sub_component('symbol references'),
        )
        self.configuration.new_sdv_checker().check(
            self.put,
            sdv,
            message_builder,
        )
        return sdv


class _IntegrationExecutionChecker(Generic[PRIMITIVE, APPLICATION_INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: APPLICATION_INPUT,
                 arrangement: Arrangement,
                 expectation: ExecutionExpectation,
                 applier: Callable[[PRIMITIVE, FullResolvingEnvironment, APPLICATION_INPUT], OUTPUT],
                 custom_properties_checker:
                 CustomExecutionPropertiesChecker[PRIMITIVE],
                 ):
        self.put = put
        self.model_constructor = model_constructor
        self.applier = applier
        self.arrangement = arrangement
        self.expectation = expectation
        self.custom_properties_checker = custom_properties_checker

        self.hds = None
        self.tcds = None

    def check(self, sut: LogicSdv[PRIMITIVE]):
        try:
            self._check(sut)
        except _CheckIsDoneException:
            pass

    def _check(self, sut: LogicSdv[PRIMITIVE]):
        message_builder = asrt.MessageBuilder('ddv')
        matcher_ddv = self._resolve_ddv(sut, message_builder)

        self.custom_properties_checker.check_ddv(
            self.put,
            matcher_ddv,
            message_builder,
        )

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

    def _check_with_hds(self, ddv: LogicDdv[PRIMITIVE]):
        self._check_validation_pre_sds(ddv)

    def _check_with_sds(self, ddv: LogicDdv[PRIMITIVE]):
        self._check_validation_post_sds(ddv)

        full_resolving_env = FullResolvingEnvironment(
            self.arrangement.symbols,
            self.tcds,
            ApplicationEnvironment(
                TmpDirFileSpaceAsDirCreatedOnDemand(self.tcds.sds.internal_tmp_dir / 'application-tmp-dir')
            ),
        )

        primitive = self._resolve_primitive_value(ddv, full_resolving_env.application_environment)

        self._check_primitive(primitive, full_resolving_env)

    def _resolve_ddv(self,
                     sdv: LogicSdv[PRIMITIVE],
                     message_builder: asrt.MessageBuilder,
                     ) -> LogicDdv[PRIMITIVE]:
        ddv = sdv.resolve(self.arrangement.symbols)

        asrt.is_instance(LogicDdv).apply(self.put,
                                         ddv,
                                         message_builder)

        assert isinstance(ddv, LogicDdv)

        return ddv

    def _resolve_primitive_value(self,
                                 ddv: LogicDdv[PRIMITIVE],
                                 application_environment: ApplicationEnvironment) -> PRIMITIVE:
        adv = ddv.value_of_any_dependency(self.tcds)

        asrt.is_instance(ApplicationEnvironmentDependentValue).apply_with_message(
            self.put,
            adv,
            'adv',
        )
        return adv.primitive(application_environment)

    def _check_validation_pre_sds(self, matcher_ddv: LogicDdv[PRIMITIVE]):
        validator = matcher_ddv.validator
        result = validator.validate_pre_sds_if_applicable(self.hds)

        self.expectation.validation.pre_sds.apply_with_message(self.put,
                                                               result,
                                                               'validation pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, matcher_ddv: LogicDdv[PRIMITIVE]):
        validator = matcher_ddv.validator
        result = validator.validate_post_sds_if_applicable(self.tcds)

        self.expectation.validation.post_sds.apply_with_message(self.put,
                                                                result,
                                                                'validation post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_primitive(self,
                         primitive: PRIMITIVE,
                         resolving_env: FullResolvingEnvironment):
        message_builder = asrt.MessageBuilder('primitive')

        self.custom_properties_checker.check_primitive(self.put,
                                                       primitive,
                                                       message_builder,
                                                       )
        try:
            result = self.applier(primitive, resolving_env, self.model_constructor)

            if self.expectation.is_hard_error is not None:
                self.put.fail(message_builder.apply('HARD_ERROR not reported (raised)'))

            self.expectation.main_result.apply(self.put, result, message_builder.for_sub_component('output'))
        except HardErrorException as ex:
            self._check_hard_error(ex, message_builder)

    def _check_hard_error(self,
                          result: HardErrorException,
                          message_builder: asrt.MessageBuilder,
                          ):
        if self.expectation.is_hard_error is None:
            self.put.fail(message_builder.apply('Unexpected HARD_ERROR'))
        else:
            self.expectation.is_hard_error.apply(self.put,
                                                 result.error,
                                                 message_builder.for_sub_component('hard error'))
            raise _CheckIsDoneException()
