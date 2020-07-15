import os
import unittest

from exactly_lib.execution import phase_step
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import instruction_environment as i
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.instructions.test_resources.instruction_check_utils import \
    InstructionExecutionBase
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents_before_main: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 previous_phase: PreviousPhase = PreviousPhase.ASSERT,
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_hds_contents=non_hds_contents_before_main,
                         tcds_contents=tcds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols,
                         fs_location_info=fs_location_info)
        self.previous_phase = previous_phase


class Expectation(ExpectationBase):
    def __init__(self,
                 act_result: SubProcessResult = SubProcessResult(),
                 validate_pre_sds_result: ValueAssertion = svh_assertions.is_success(),
                 main_result: ValueAssertion = sh_assertions.is_success(),
                 symbol_usages: ValueAssertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: ValueAssertion = asrt.anything_goes(),
                 main_side_effects_on_tcds: ValueAssertion = asrt.anything_goes(),
                 source: ValueAssertion = asrt.anything_goes(),
                 ):
        super().__init__(validate_pre_sds_result,
                         main_side_effects_on_sds,
                         main_side_effects_on_tcds,
                         symbol_usages)
        self.act_result = act_result
        self.main_result = main_result
        self.source = source


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
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        self._check_instruction(CleanupPhaseInstruction, instruction)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, CleanupPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
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

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                environment = InstructionEnvironmentForPreSdsStep(tcds.hds,
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
                tcds.sds,
                phase_identifier.CLEANUP.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)

            self._execute_main(environment, instruction)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _execute_pre_validate(self,
                              environment: InstructionEnvironmentForPreSdsStep,
                              instruction: CleanupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(environment)
        self._check_result_of_validate_pre_sds(result)
        self.expectation.validation_pre_sds.apply(self.put, result)
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: CleanupPhaseInstruction) -> sh.SuccessOrHardError:
        result = instruction.main(environment,
                                  self.arrangement.os_services,
                                  self.arrangement.previous_phase)
        self._check_result_of_main__sh(result)
        self.expectation.main_result.apply(self.put, result)
        return result
