import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.instructions.test_resources.instruction_check_utils import \
    InstructionExecutionBase
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_utils.test_resources import svh_assertions, sh_assertions
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import utils
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction, home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_home_contents_before_main: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 previous_phase: PreviousPhase = PreviousPhase.ASSERT,
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 symbols: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         home_contents=home_dir_contents,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_home_contents=non_home_contents_before_main,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         home_or_sds_contents=home_or_sds_contents,
                         symbols=symbols)
        self.previous_phase = previous_phase


class Expectation(ExpectationBase):
    def __init__(self,
                 act_result: utils.ActResult = utils.ActResult(),
                 validate_pre_sds_result: asrt.ValueAssertion = svh_assertions.is_success(),
                 main_result: asrt.ValueAssertion = sh_assertions.is_success(),
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                 side_effects_check: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        super().__init__(validate_pre_sds_result,
                         main_side_effects_on_files,
                         side_effects_check)
        self.act_result = act_result
        self.validate_pre_sds_result = validate_pre_sds_result
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check
        self.source = source
        self.symbol_usages = symbol_usages


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: InstructionParser,
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
                parser: InstructionParser,
                source: ParseSource):
        instruction = parser.parse(source)
        self._check_instruction(CleanupPhaseInstruction, instruction)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, CleanupPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
                                                          'symbol-usages after parse')
        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                home_dir_contents=self.arrangement.home_contents,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            home_and_sds = path_resolving_environment.home_and_sds
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds,
                                                              self.arrangement.process_execution_settings.environ,
                                                              symbols=self.arrangement.symbols)
            result_of_validate_pre_sds = self._execute_pre_validate(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_PRE_SDS)
            if not result_of_validate_pre_sds.is_success:
                return
            environment = i.InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                home_and_sds.sds,
                phase_identifier.CLEANUP.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.sds)
            self.expectation.side_effects_check.apply(self.put, home_and_sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _execute_pre_validate(self,
                              environment: InstructionEnvironmentForPreSdsStep,
                              instruction: CleanupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(environment)
        self._check_result_of_validate_pre_sds(result)
        self.expectation.validate_pre_sds_result.apply(self.put, result)
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: CleanupPhaseInstruction) -> sh.SuccessOrHardError:
        result = instruction.main(environment,
                                  self.arrangement.os_services,
                                  self.arrangement.previous_phase)
        self._check_result_of_main__sh(result)
        self.expectation.main_result.apply(self.put, result)
        self.expectation.main_side_effects_on_files.apply(self.put, environment.sds)
        return result
