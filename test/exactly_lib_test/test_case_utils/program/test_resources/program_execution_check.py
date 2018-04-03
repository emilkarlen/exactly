import pathlib
import pathlib
import unittest
from typing import Optional

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds, PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import ExecutorThatStoresResultInFilesInDir
from exactly_lib.util import file_utils
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_no_timeout, Command
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.instructions.test_resources.instruction_check_utils import \
    InstructionExecutionBase
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.execution import tmp_dir
from exactly_lib_test.test_resources.execution.utils import ProcessResult
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction, home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder


def assert_process_result(exitcode: asrt.ValueAssertion[int] = asrt.anything_goes(),
                          stdout_contents: asrt.ValueAssertion[str] = asrt.anything_goes(),
                          stderr_contents: asrt.ValueAssertion[str] = asrt.anything_goes()
                          ) -> asrt.ValueAssertion[ProcessResult]:
    return ProcessResultAssertion(exitcode, stdout_contents, stderr_contents)


class ProcessResultAssertion(asrt.ValueAssertion[ProcessResult]):
    def __init__(self,
                 exitcode: asrt.ValueAssertion[int] = asrt.anything_goes(),
                 stdout_contents: asrt.ValueAssertion[str] = asrt.anything_goes(),
                 stderr_contents: asrt.ValueAssertion[str] = asrt.anything_goes()
                 ):
        self.exitcode = exitcode
        self.stdout_contents = stdout_contents
        self.stderr_contents = stderr_contents

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value, ProcessResult,
                             message_builder.apply("result object class"))
        assert isinstance(value, ProcessResult)  # Type info for IDE
        self.exitcode.apply(put,
                            value.exitcode,
                            message_builder.for_sub_component('exitcode'))
        self.stdout_contents.apply(put,
                                   value.stdout_contents,
                                   message_builder.for_sub_component('stdout'))
        self.stderr_contents.apply(put,
                                   value.stderr_contents,
                                   message_builder.for_sub_component('stderr'))


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_home_contents_before_main: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 previous_phase: PreviousPhase = PreviousPhase.ASSERT,
                 symbols: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_home_contents=non_home_contents_before_main,
                         home_or_sds_contents=home_or_sds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols)
        self.previous_phase = previous_phase


class Expectation(ExpectationBase):
    def __init__(self,
                 result: asrt.ValueAssertion[ProcessResult] = assert_process_result(),
                 validate_pre_sds: asrt.ValueAssertion[str] = asrt.is_none,
                 validate_post_sds: asrt.ValueAssertion[str] = asrt.is_none,
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 main_side_effects_on_home_and_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        super().__init__(validate_pre_sds,
                         main_side_effects_on_sds,
                         main_side_effects_on_home_and_sds,
                         symbol_usages)
        self.validate_post_sds = validate_post_sds
        self.result = result
        self.source = source


is_success = Expectation


def check(put: unittest.TestCase,
          parser: Parser[ProgramResolver],
          source: ParseSource,
          arrangement: Arrangement,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: Parser[ProgramResolver],
                source: ParseSource):
        program_resolver = parser.parse(source)
        self._check_instruction(ProgramResolver, program_resolver)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(program_resolver, ProgramResolver)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          program_resolver.symbol_usages(),
                                                          'symbol-usages after parse')
        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            with tmp_dir.tmp_dir() as pgm_output_dir:
                self.check(pgm_output_dir, path_resolving_environment, program_resolver)

    def check(self,
              pgm_output_dir: pathlib.Path,
              environment: PathResolvingEnvironmentPreOrPostSds,
              program_resolver: ProgramResolver):

        result = self._execute_pre_validate(environment,
                                            program_resolver)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          program_resolver.symbol_usages(),
                                                          'symbol-usages after ' +
                                                          phase_step.STEP__VALIDATE_PRE_SDS)
        if result is not None:
            return

        result = self._execute_post_sds_validate(environment, program_resolver)
        if result is not None:
            return
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          program_resolver.symbol_usages(),
                                                          'symbol-usages after' +
                                                          phase_step.STEP__VALIDATE_POST_SETUP)

        self._execute_program(pgm_output_dir, environment, program_resolver)

    def _execute_pre_validate(self,
                              environment: PathResolvingEnvironmentPreSds,
                              program_resolver: ProgramResolver) -> Optional[str]:
        actual = program_resolver.validator.validate_pre_sds_if_applicable(environment)
        self.expectation.validation_pre_sds.apply_with_message(self.put, actual, 'validation-pre-sds')
        return actual

    def _execute_post_sds_validate(self,
                                   environment: PathResolvingEnvironmentPostSds,
                                   program_resolver: ProgramResolver) -> Optional[str]:
        actual = program_resolver.validator.validate_post_sds_if_applicable(environment)
        self.expectation.validate_post_sds.apply_with_message(self.put, actual, 'validation-post-sds')
        return actual

    def _execute_program(self,
                         pgm_output_dir: pathlib.Path,
                         environment: PathResolvingEnvironmentPreOrPostSds,
                         program_resolver: ProgramResolver):
        result = self._execute(pgm_output_dir, environment, program_resolver)

        self.expectation.result.apply(self.put, result)
        self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
        self.expectation.main_side_effects_on_home_and_sds.apply(self.put, environment.home_and_sds)

    def _execute(self,
                 pgm_output_dir: pathlib.Path,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 program_resolver: ProgramResolver) -> ProcessResult:
        command = program_resolver.resolve_value(environment.symbols).value_of_any_dependency(environment.home_and_sds)
        assert isinstance(command, Command)
        executor = ExecutorThatStoresResultInFilesInDir(self.arrangement.process_execution_settings)
        execution_result = executor.apply(pgm_output_dir, command)
        stderr_contents = file_utils.contents_of(execution_result.path_of(ProcOutputFile.STDERR))
        stdout_contents = file_utils.contents_of(execution_result.path_of(ProcOutputFile.STDOUT))
        return ProcessResult(execution_result.exit_code,
                             stdout_contents,
                             stderr_contents)
