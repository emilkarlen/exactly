import os
import unittest
from typing import Sequence

from exactly_lib.execution import phase_step
from exactly_lib.impls.os_services.os_services_access import new_for_current_os
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import sh, svh
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources.predefined_properties import get_empty_environ
from exactly_lib_test.impls.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.impls.instructions.test_resources.instruction_check_utils import \
    InstructionExecutionBase
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import instruction_settings as instr_settings
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents_before_main: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = new_for_current_os(),
                 process_execution_settings: ProcessExecutionSettings = ProcessExecutionSettings.null(),
                 default_environ_getter: DefaultEnvironGetter = get_empty_environ,
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
                         default_environ_getter=default_environ_getter,
                         symbols=symbols,
                         fs_location_info=fs_location_info)
        self.previous_phase = previous_phase


class MultiSourceExpectation(ExpectationBase):
    def __init__(self,
                 act_result: SubProcessResult = SubProcessResult(),
                 validate_pre_sds_result: Assertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 main_result: Assertion[sh.SuccessOrHardError] = sh_assertions.is_success(),
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 ):
        super().__init__(validate_pre_sds_result,
                         main_side_effects_on_sds,
                         main_side_effects_on_tcds,
                         symbol_usages,
                         proc_exe_settings,
                         instruction_settings)
        self._act_result = act_result
        self._main_result = main_result

    @property
    def act_result(self) -> SubProcessResult:
        return self._act_result

    @property
    def main_result(self) -> Assertion[sh.SuccessOrHardError]:
        return self._main_result


class Expectation(MultiSourceExpectation):
    def __init__(self,
                 act_result: SubProcessResult = SubProcessResult(),
                 validate_pre_sds_result: Assertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 main_result: Assertion[sh.SuccessOrHardError] = sh_assertions.is_success(),
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
                 source: Assertion[ParseSource] = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 ):
        super().__init__(act_result,
                         validate_pre_sds_result,
                         main_result,
                         symbol_usages,
                         main_side_effects_on_sds,
                         main_side_effects_on_tcds,
                         proc_exe_settings,
                         instruction_settings)
        self._source = source

    @property
    def source(self) -> Assertion[ParseSource]:
        return self._source


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
        self.expectation.source.apply_with_message(self.put, source, 'source')
        InstructionCheckExecutor(self.put, self.arrangement, self.expectation).check(instruction)


class CleanupInstructionChecker(InstructionChecker[Arrangement, MultiSourceExpectation]):
    def check(self,
              put: unittest.TestCase,
              instruction: Instruction,
              arrangement: Arrangement,
              expectation: MultiSourceExpectation):
        InstructionCheckExecutor(put, arrangement, expectation).check(instruction)


class InstructionCheckExecutor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: MultiSourceExpectation):
        super().__init__(put, arrangement, expectation)
        self.arrangement = arrangement
        self.expectation = expectation

    def check(self, instruction: Instruction):
        self._check_instruction(CleanupPhaseInstruction, instruction)
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
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                tcds,
                self.arrangement.symbols,
                self.arrangement.process_execution_settings,
            )

            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                environment = environment_builder.build_pre_sds()

                result_of_validate_pre_sds = self._execute_pre_validate(environment, instruction)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  instruction.symbol_usages(),
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if not result_of_validate_pre_sds.is_success:
                    return

            environment = environment_builder.build_post_sds()
            instruction_settings = instr_settings.from_proc_exe_settings(self.arrangement.process_execution_settings,
                                                                         self.arrangement.default_environ_getter)

            result_of_main = self._execute_main(environment, instruction_settings, instruction)

            self.expectation.instruction_settings.apply_with_message(self.put, instruction_settings,
                                                                     'instruction settings')
            self.expectation.proc_exe_settings.apply_with_message(self.put, environment.proc_exe_settings,
                                                                  'proc exe settings')
            self.expectation.main_side_effects_on_sds.apply_with_message(self.put, environment.sds, 'SDS')
            self.expectation.main_side_effects_on_tcds.apply_with_message(self.put, tcds, 'TCDS')

        self.expectation.main_result.apply_with_message(self.put, result_of_main,
                                                        'result of main (without access to TCDS)')

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
                      settings: InstructionSettings,
                      instruction: CleanupPhaseInstruction) -> sh.SuccessOrHardError:
        result = instruction.main(environment,
                                  settings,
                                  self.arrangement.os_services,
                                  self.arrangement.previous_phase)
        self._check_result_of_main__sh(result)
        return result
