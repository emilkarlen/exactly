import pathlib
import unittest
from typing import Optional, Sequence, Dict, Generic

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.execution import phase_step
from exactly_lib.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryoParser, \
    InstructionEmbryo, T
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_case_utils.test_resources import validation as validation_utils
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, ValidationResultAssertion
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              tcds: TestCaseDs):
        pass


class InstructionApplicationEnvironment:
    def __init__(self,
                 os_service: OsServices,
                 instruction: InstructionEnvironmentForPostSdsStep,
                 ):
        self._os_service = os_service
        self._instruction = instruction

    @property
    def os_service(self) -> OsServices:
        return self._os_service

    @property
    def instruction(self) -> InstructionEnvironmentForPostSdsStep:
        return self._instruction


class Expectation(Generic[T]):
    def __init__(self,
                 validation_pre_sds: ValidationResultAssertion = asrt.is_none,
                 validation_post_sds: ValidationResultAssertion = asrt.is_none,
                 main_result: ValueAssertion[T] = asrt.anything_goes(),
                 main_raises_hard_error: bool = False,
                 symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 symbols_after_main: ValueAssertion[SymbolTable] = asrt.anything_goes(),
                 main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
                 side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
                 side_effects_on_hds: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
                 source: ValueAssertion[ParseSource] = asrt.anything_goes(),
                 main_side_effect_on_environment_variables: ValueAssertion[Dict[str, str]] = asrt.anything_goes(),
                 assertion_on_instruction_environment:
                 ValueAssertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
                 ):
        self.validation_pre_sds = validation_pre_sds
        self.validation_post_sds = validation_post_sds
        self.main_result = main_result
        self.main_raises_hard_error = main_raises_hard_error
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.side_effects_on_tcds = side_effects_on_tcds
        self.side_effects_on_hds = side_effects_on_hds
        self.source = source
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main
        self.main_side_effect_on_environment_variables = main_side_effect_on_environment_variables
        self.instruction_application_environment = assertion_on_instruction_environment


def expectation(validation: ValidationAssertions = validation_utils.all_validations_passes(),
                main_result: ValueAssertion[T] = asrt.anything_goes(),
                main_raises_hard_error: bool = False,
                symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                symbols_after_main: ValueAssertion[SymbolTable] = asrt.anything_goes(),
                main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
                side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
                side_effects_on_home: ValueAssertion[pathlib.Path] = asrt.anything_goes(),
                source: ValueAssertion[ParseSource] = asrt.anything_goes(),
                main_side_effect_on_environment_variables: ValueAssertion[Dict[str, str]] = asrt.anything_goes(),
                assertion_on_instruction_environment:
                ValueAssertion[InstructionApplicationEnvironment] = asrt.anything_goes(),
                ) -> Expectation[T]:
    return Expectation(
        validation_pre_sds=validation.pre_sds,
        validation_post_sds=validation.post_sds,
        main_result=main_result,
        main_raises_hard_error=main_raises_hard_error,
        symbol_usages=symbol_usages,
        symbols_after_main=symbols_after_main,
        main_side_effects_on_sds=main_side_effects_on_sds,
        side_effects_on_tcds=side_effects_on_tcds,
        side_effects_on_hds=side_effects_on_home,
        source=source,
        main_side_effect_on_environment_variables=main_side_effect_on_environment_variables,
        assertion_on_instruction_environment=assertion_on_instruction_environment,
    )


class TestCaseBase(Generic[T], unittest.TestCase):
    def _check(self,
               parser: InstructionEmbryoParser[T],
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation[T]):
        check(self,
              parser,
              source,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          parser: InstructionEmbryoParser[T],
          source: ParseSource,
          arrangement: ArrangementWithSds,
          expectation: Expectation[T]):
    Executor(put, arrangement, expectation).execute(parser, source)


class Checker(Generic[T]):
    def __init__(self, parser: InstructionEmbryoParser[T]):
        self.parser = parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: ArrangementWithSds,
              expectation: Expectation[T],
              ):
        Executor(put, arrangement, expectation).execute(self.parser, source)

    def check__w_source_variants(self,
                                 put: unittest.TestCase,
                                 source: str,
                                 arrangement: ArrangementWithSds,
                                 expectation: Expectation,
                                 ):
        for source in equivalent_source_variants__with_source_check__consume_last_line(put, source):
            Executor(put, arrangement, expectation).execute(self.parser, source)


class Executor(Generic[T]):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementWithSds,
                 expectation: Expectation[T]):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def execute(self,
                parser: InstructionEmbryoParser,
                source: ParseSource):
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        asrt.is_instance(InstructionEmbryo).apply_with_message(self.put, instruction,
                                                               'Instruction class')
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, InstructionEmbryo)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages,
                                                          'symbol-usages after parse')
        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            tcds = path_resolving_environment.tcds
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                tcds,
                self.arrangement.symbols,
                ProcessExecutionSettings(
                    timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                    environ=_initial_environment_variables_dict(self.arrangement),
                ),
            )

            environment = environment_builder.build_pre_sds()
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_PRE_SDS)
            if validate_result is not None:
                return
            environment = environment_builder.build_post_sds()
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            result_of_main = self._execute_main(environment, instruction)

            self.expectation.main_side_effects_on_sds.apply_with_message(self.put, tcds.sds,
                                                                         'side_effects_on_files')
            self.expectation.side_effects_on_tcds.apply_with_message(self.put, tcds,
                                                                     'side_effects_on_tcds')
            self.expectation.main_side_effect_on_environment_variables.apply_with_message(
                self.put,
                environment.proc_exe_settings.environ,
                'main side effects on environment variables')
            self.expectation.symbols_after_main.apply_with_message(
                self.put,
                environment.symbols,
                'symbols_after_main')
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
            self.expectation.side_effects_on_hds.apply_with_message(self.put, tcds.hds.case_dir,
                                                                    'side_effects_on_home')

            application_environment = InstructionApplicationEnvironment(
                self.arrangement.os_services,
                environment
            )
            self.expectation.instruction_application_environment.apply_with_message(self.put,
                                                                                    application_environment,
                                                                                    'assertion_on_environment')
            self.expectation.main_result.apply_with_message(self.put, result_of_main,
                                                            'result of main (wo access to TCDS)')

    def _execute_validate_pre_sds(
            self,
            environment: InstructionEnvironmentForPreSdsStep,
            instruction: InstructionEmbryo[T]) -> Optional[TextRenderer]:
        result = instruction.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation_pre_sds.apply_with_message(self.put, result,
                                                               'validation_pre_sds')
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: InstructionEmbryo[T]) -> Optional[TextRenderer]:
        result = instruction.validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation_post_sds.apply_with_message(self.put, result,
                                                                'validation_post_sds')
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: InstructionEmbryo[T]) -> T:
        try:
            result = instruction.main(environment,
                                      self.arrangement.os_services)
        except HardErrorException as ex:
            if self.expectation.main_raises_hard_error:
                text_doc_assertions.assert_is_valid_text_renderer(self.put, ex.error)
                return
            else:
                self.put.fail('unexpected {} from main'.format(HardErrorException))

        if self.expectation.main_raises_hard_error:
            self.put.fail('main does not raise ' + str(HardErrorException))

        return result


def _initial_environment_variables_dict(arrangement: ArrangementWithSds) -> Dict[str, str]:
    environ = arrangement.process_execution_settings.environ
    if environ is None:
        environ = {}
    return environ
