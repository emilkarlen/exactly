"""
Tools for integration testing of logic values the use the XDV-structure:

 - SDV
 - DDV
 - ADV
 - primitive
"""
import unittest
from contextlib import contextmanager
from typing import Sequence, Generic, ContextManager, Callable, TypeVar

from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.app_env_dep_ddv import LogicDdv
from exactly_lib.type_val_deps.dep_variants.sdv.logic_type_sdv import LogicSdv
from exactly_lib.type_val_deps.envs.resolving_environment import FullResolvingEnvironment
from exactly_lib_test.tcfs.test_resources.ds_construction import tcds_with_act_as_curr_dir_3
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_case_utils.logic.test_resources.common_properties_checker import \
    CommonPropertiesConfiguration, CommonExecutionPropertiesChecker, OUTPUT, INPUT, PRIMITIVE, Applier
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, PrimAndExeExpectation, Expectation, MultiSourceExpectation, AssertionResolvingEnvironment
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser, \
    equivalent_source_variants__with_source_check__for_expression_parser_2, \
    equivalent_source_variants__with_source_check__for_full_line_expression_parser
from exactly_lib_test.test_resources.test_utils import NExArr, NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces


class IntegrationChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    """
    Tests object of a single type.

    A single instance may be used for multiple tests.
    """

    def __init__(self,
                 parser: Parser[LogicSdv[PRIMITIVE]],
                 configuration: CommonPropertiesConfiguration[PRIMITIVE, INPUT, OUTPUT],
                 check_application_result_with_tcds: bool,
                 ):
        """
        :param parser: Parser of objects of the tested type.
        :param configuration: Properties common to all objects of the tested type.
        """
        self._parser = parser
        self._configuration = configuration
        self._check_application_result_with_tcds = check_application_result_with_tcds

    @property
    def parser(self) -> Parser[LogicSdv[PRIMITIVE]]:
        return self._parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              input_: INPUT,
              arrangement: Arrangement,
              expectation: Expectation[PRIMITIVE, OUTPUT],
              ):
        checker = _ParseAndExecutionChecker(put,
                                            input_,
                                            self._parser,
                                            arrangement,
                                            self._configuration,
                                            self._check_application_result_with_tcds,
                                            expectation)
        checker.check(source)

    def check__w_source_variants(self,
                                 put: unittest.TestCase,
                                 arguments: Arguments,
                                 input_: INPUT,
                                 arrangement: Arrangement,
                                 expectation: Expectation[PRIMITIVE, OUTPUT],
                                 ):
        for source in equivalent_source_variants__with_source_check__for_expression_parser(
                put, arguments):
            self.check(put, source, input_, arrangement, expectation)

    def check__w_source_variants_for_full_line_parser_2(self,
                                                        put: unittest.TestCase,
                                                        arguments: Arguments,
                                                        input_: INPUT,
                                                        arrangement: Arrangement,
                                                        expectation: Expectation[PRIMITIVE, OUTPUT],
                                                        ):
        self.check__w_source_variants_for_full_line_parser(
            put,
            arguments,
            input_,
            arrangement,
            MultiSourceExpectation(
                expectation.parse.symbol_references,
                expectation.execution,
                expectation.primitive,
            )
        )

    def check__w_source_variants_for_full_line_parser(self,
                                                      put: unittest.TestCase,
                                                      arguments: Arguments,
                                                      input_: INPUT,
                                                      arrangement: Arrangement,
                                                      expectation: MultiSourceExpectation[PRIMITIVE, OUTPUT]
                                                      ):
        checker = _ExecutionChecker(put,
                                    input_,
                                    arrangement,
                                    expectation.primitive,
                                    expectation.execution,
                                    self._configuration.applier(),
                                    self._configuration.new_execution_checker(),
                                    self._check_application_result_with_tcds,
                                    )
        for case in equivalent_source_variants__with_source_check__for_full_line_expression_parser(arguments):
            with put.subTest(case.name):
                source = case.actual

                actual_sdv = self._parser.parse(source)

                case.expected.apply_with_message(put, source, 'source after parse')
                self._check_sdv(put, actual_sdv, expectation.symbol_references)

                checker.check(actual_sdv)

    def check_multi(self,
                    put: unittest.TestCase,
                    arguments: Arguments,
                    parse_expectation: ParseExpectation,
                    input_: INPUT,
                    execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                               Arrangement]],
                    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')
        self._check_sdv(put, actual, parse_expectation.symbol_references)

        for case in execution:
            with put.subTest(case.name):
                checker = _ExecutionChecker(put,
                                            input_,
                                            case.arrangement,
                                            case.expected.primitive,
                                            case.expected.execution,
                                            self._configuration.applier(),
                                            self._configuration.new_execution_checker(),
                                            self._check_application_result_with_tcds,
                                            )
                checker.check(actual)

    def check_multi__w_source_variants(self,
                                       put: unittest.TestCase,
                                       arguments: Arguments,
                                       symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                       input_: INPUT,
                                       execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                                                  Arrangement]],
                                       ):
        self._check_multi__w_source_variants(
            put,
            symbol_references,
            input_,
            equivalent_source_variants__with_source_check__for_expression_parser_2(arguments),
            execution,
        )

    def check_multi__w_source_variants_for_full_line_parser(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            input_: INPUT,
            symbol_references: ValueAssertion[Sequence[SymbolReference]],
            execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                       Arrangement]],
    ):
        self._check_multi__w_source_variants(
            put,
            symbol_references,
            input_,
            equivalent_source_variants__with_source_check__for_full_line_expression_parser(arguments),
            execution,
        )

    def check_single_multi_execution_setup__for_test_of_test_resources(
            self,
            put: unittest.TestCase,
            arguments: Arguments,
            parse_expectation: ParseExpectation,
            model_constructor: INPUT,
            execution: NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT], Arrangement],
    ):
        source = arguments.as_remaining_source
        actual = self._parser.parse(source)
        parse_expectation.source.apply_with_message(put, source, 'source after parse')

        self._check_sdv(put, actual, parse_expectation.symbol_references)

        checker = _ExecutionChecker(put,
                                    model_constructor,
                                    execution.arrangement,
                                    execution.expected.primitive,
                                    execution.expected.execution,
                                    self._configuration.applier(),
                                    self._configuration.new_execution_checker(),
                                    self._check_application_result_with_tcds,
                                    )
        checker.check(actual)

    def _check_multi__w_source_variants(
            self,
            put: unittest.TestCase,
            symbol_references: ValueAssertion[Sequence[SymbolReference]],
            input_: INPUT,
            source_cases: Sequence[NEA[ValueAssertion[ParseSource], ParseSource]],
            execution: Sequence[NExArr[PrimAndExeExpectation[PRIMITIVE, OUTPUT],
                                       Arrangement]],
    ):
        for source_case in source_cases:
            with put.subTest(source_case.name):
                source = source_case.actual
                actual = self._parser.parse(source)
                source_case.expected.apply_with_message(put, source, 'source after parse')
                self._check_sdv(put, actual, symbol_references)

                for case in execution:
                    with put.subTest(source_case=source_case.name,
                                     execution_case=case.name):
                        checker = _ExecutionChecker(put,
                                                    input_,
                                                    case.arrangement,
                                                    case.expected.primitive,
                                                    case.expected.execution,
                                                    self._configuration.applier(),
                                                    self._configuration.new_execution_checker(),
                                                    self._check_application_result_with_tcds,
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


class _ParseAndExecutionChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: INPUT,
                 parser: Parser[LogicSdv[PRIMITIVE]],
                 arrangement: Arrangement,
                 configuration: CommonPropertiesConfiguration[PRIMITIVE, INPUT, OUTPUT],
                 check_application_result_with_tcds: bool,
                 expectation: Expectation[PRIMITIVE, OUTPUT],
                 ):
        self.put = put
        self.parser = parser
        self.configuration = configuration
        self.expectation = expectation
        self.source_expectation = expectation.parse.source
        self._execution_checker = _ExecutionChecker(put,
                                                    model_constructor,
                                                    arrangement,
                                                    expectation.primitive,
                                                    expectation.execution,
                                                    configuration.applier(),
                                                    configuration.new_execution_checker(),
                                                    check_application_result_with_tcds,
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


T = TypeVar('T')


class _ValueAssertionApplier:
    def __init__(self,
                 assertion: ValueAssertion[T],
                 value: T,
                 message_builder: asrt.MessageBuilder,
                 ):
        self.assertion = assertion
        self.value = value
        self.message_builder = message_builder

    def apply(self, put: unittest.TestCase):
        self.assertion.apply(put, self.value, self.message_builder)


class _ExecutionChecker(Generic[PRIMITIVE, INPUT, OUTPUT]):
    FAKE_TCDS = fake_tcds()

    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: INPUT,
                 arrangement: Arrangement,
                 primitive: Callable[[AssertionResolvingEnvironment], ValueAssertion[PRIMITIVE]],
                 execution: ExecutionExpectation[OUTPUT],
                 applier: Applier[PRIMITIVE, INPUT, OUTPUT],
                 common_properties:
                 CommonExecutionPropertiesChecker[PRIMITIVE, OUTPUT],
                 check_application_result_with_tcds: bool,
                 ):
        self.put = put
        self.model_constructor = model_constructor
        self.applier = applier
        self.arrangement = arrangement
        self.primitive = primitive
        self.execution = execution
        self.common_properties = common_properties
        self.check_application_result_with_tcds = check_application_result_with_tcds

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

        self.common_properties.check_ddv(
            self.put,
            matcher_ddv,
            message_builder,
        )

        with self._tcds_with_act_as_curr_dir() as tcds:
            self.hds = tcds.hds

            self._check_with_hds(matcher_ddv)

            self.tcds = tcds

            application_result_assertion = self._check_with_sds(matcher_ddv)

            if self.check_application_result_with_tcds:
                application_result_assertion.apply(self.put)

        if not self.check_application_result_with_tcds:
            application_result_assertion.apply(self.put)

    def _tcds_with_act_as_curr_dir(self) -> ContextManager[TestCaseDs]:
        tcds_arrangement = self.arrangement.tcds
        return (
            tcds_with_act_as_curr_dir_3(tcds_arrangement)
            if tcds_arrangement
            else
            self._dummy_tcds_setup()
        )

    @contextmanager
    def _dummy_tcds_setup(self) -> ContextManager[TestCaseDs]:
        yield self.FAKE_TCDS

    def _check_with_hds(self, ddv: LogicDdv[PRIMITIVE]):
        self._check_validation_pre_sds(ddv)

    def _check_with_sds(self, ddv: LogicDdv[PRIMITIVE]) -> _ValueAssertionApplier:
        self._check_validation_post_sds(ddv)

        full_resolving_env = FullResolvingEnvironment(
            self.arrangement.symbols,
            self.tcds,
            ApplicationEnvironment(
                self.arrangement.process_execution.os_services,
                self.arrangement.process_execution.process_execution_settings,
                tmp_file_spaces.tmp_dir_file_space_for_test(
                    self.tcds.sds.internal_tmp_dir / 'application-tmp-dir')
            ),
        )

        primitive = self._resolve_primitive_value(ddv, full_resolving_env.application_environment)

        return self._check_primitive(primitive, full_resolving_env)

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

        self.execution.validation.pre_sds.apply_with_message(self.put,
                                                             result,
                                                             'validation pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, matcher_ddv: LogicDdv[PRIMITIVE]):
        validator = matcher_ddv.validator
        result = validator.validate_post_sds_if_applicable(self.tcds)

        self.execution.validation.post_sds.apply_with_message(self.put,
                                                              result,
                                                              'validation post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_primitive(self,
                         primitive: PRIMITIVE,
                         resolving_env: FullResolvingEnvironment,
                         ) -> _ValueAssertionApplier:
        message_builder = asrt.MessageBuilder('primitive')

        self.common_properties.check_primitive(self.put,
                                               primitive,
                                               message_builder,
                                               )
        assertion_on_primitive = self.primitive(AssertionResolvingEnvironment(resolving_env.tcds,
                                                                              resolving_env.application_environment))
        assertion_on_primitive.apply(self.put, primitive, message_builder)

        try:
            result = self.applier.apply(self.put, message_builder, primitive, resolving_env, self.model_constructor)

            if self.execution.is_hard_error is not None:
                self.put.fail(message_builder.apply('HARD_ERROR not reported (raised)'))

            self.common_properties.check_application_output(
                self.put,
                result,
                message_builder.for_sub_component('common properties of output')
            )
            return _ValueAssertionApplier(
                self.execution.main_result,
                result,
                message_builder.for_sub_component('output'),
            )
        except HardErrorException as ex:
            return self._check_hard_error(ex, message_builder)

    def _check_hard_error(self,
                          result: HardErrorException,
                          message_builder: asrt.MessageBuilder,
                          ) -> _ValueAssertionApplier:
        if self.execution.is_hard_error is None:
            self.put.fail(message_builder.apply('Unexpected HARD_ERROR'))
        else:
            return _ValueAssertionApplier(
                self.execution.is_hard_error,
                result.error,
                message_builder.for_sub_component('hard error'),
            )
