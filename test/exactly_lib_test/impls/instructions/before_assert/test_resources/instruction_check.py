import os
import unittest

from exactly_lib.execution import phase_step
from exactly_lib.impls.os_services.os_services_access import new_for_current_os
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
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
from exactly_lib_test.impls.instructions.test_resources.instruction_check_utils import InstructionExecutionBase
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.tcfs.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import instruction_settings as instr_settings
from exactly_lib_test.test_case.test_resources.act_result import ActEnvironment, ActResultProducer, \
    ActResultProducerFromActResult
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def arrangement(pre_contents_population_action: TcdsAction = TcdsAction(),
                hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                non_hds_contents_before_main: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                os_services: OsServices = new_for_current_os(),
                process_execution_settings: ProcessExecutionSettings = ProcessExecutionSettings.null(),
                default_environ_getter: DefaultEnvironGetter = get_empty_environ,
                symbols: SymbolTable = None,
                ) -> ArrangementPostAct:
    return ArrangementPostAct(pre_contents_population_action=pre_contents_population_action,
                              hds_contents=hds_contents,
                              sds_contents=sds_contents_before_main,
                              non_hds_contents=non_hds_contents_before_main,
                              tcds_contents=tcds_contents,
                              act_result_producer=act_result_producer,
                              os_services=os_services,
                              process_execution_settings=process_execution_settings,
                              default_environ_getter=default_environ_getter,
                              symbols=symbols)


class MultiSourceExpectation(ExpectationBase):
    def __init__(self,
                 validation_pre_sds: Assertion = svh_assertions.is_success(),
                 validation_post_setup: Assertion = svh_assertions.is_success(),
                 main_result: Assertion = sh_assertions.is_success(),
                 symbol_usages: Assertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 ):
        super().__init__(validation_pre_sds,
                         main_side_effects_on_sds,
                         main_side_effects_on_tcds,
                         symbol_usages,
                         proc_exe_settings,
                         instruction_settings)
        self.validation_post_setup = validation_post_setup
        self.main_result = sh_assertions.is_sh_and(main_result)


class Expectation(MultiSourceExpectation):
    def __init__(self,
                 validation_pre_sds: Assertion = svh_assertions.is_success(),
                 validation_post_setup: Assertion = svh_assertions.is_success(),
                 main_result: Assertion[sh.SuccessOrHardError] = sh_assertions.is_success(),
                 symbol_usages: Assertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion = asrt.anything_goes(),
                 source: Assertion = asrt.anything_goes(),
                 proc_exe_settings: Assertion[ProcessExecutionSettings]
                 = asrt.is_instance(ProcessExecutionSettings),
                 instruction_settings: Assertion[InstructionSettings]
                 = asrt.is_instance(InstructionSettings),
                 ):
        super().__init__(validation_pre_sds,
                         validation_post_setup,
                         main_result,
                         symbol_usages,
                         main_side_effects_on_sds,
                         main_side_effects_on_tcds,
                         proc_exe_settings,
                         instruction_settings,
                         )
        self.source = source


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: InstructionParser,
          source: ParseSource,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def _check(self,
               component: str,
               assertion: Assertion,
               actual):
        assertion.apply(self.put,
                        actual,
                        asrt.MessageBuilder(component))
        return actual

    def execute(self,
                parser: InstructionParser,
                source: ParseSource):
        instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        instruction_checker = _InstructionCheckExecutor(self.put, self.arrangement, self.expectation)
        instruction_checker.check(instruction)


class BeforeAssertInstructionChecker(InstructionChecker[ArrangementPostAct, MultiSourceExpectation]):
    def check(self,
              put: unittest.TestCase,
              instruction: Instruction,
              arrangement: ArrangementPostAct,
              expectation: MultiSourceExpectation):
        _InstructionCheckExecutor(put, arrangement, expectation).check(instruction)


class _InstructionCheckExecutor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: MultiSourceExpectation):
        super().__init__(put, arrangement, expectation)
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def check(self, instruction: Instruction):
        self._check_instruction(BeforeAssertPhaseInstruction, instruction)
        assert isinstance(instruction, BeforeAssertPhaseInstruction)
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

                validate_result = self._execute_validate_pre_sds(environment, instruction)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  instruction.symbol_usages(),
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if not validate_result.is_success:
                    return

            environment = environment_builder.build_post_sds()
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if not validate_result.is_success:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(tcds))
            write_act_result(tcds.sds, act_result)

            instruction_settings = instr_settings.from_proc_exe_settings(self.arrangement.process_execution_settings,
                                                                         self.arrangement.default_environ_getter)

            result_from_main = self._execute_main(environment, instruction_settings, instruction)

            self.expectation.instruction_settings.apply_with_message(self.put,
                                                                     instruction_settings,
                                                                     'instruction settings')
            self._check_main_side_effects_on_sds(tcds)
            self._check_side_effects_on_tcds(tcds)
            self.expectation.proc_exe_settings.apply_with_message(self.put,
                                                                  environment.proc_exe_settings,
                                                                  'proc exe settings')
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
        self._check('result from main (without access to TCDS)',
                    self.expectation.main_result,
                    result_from_main)

    def _execute_validate_pre_sds(
            self,
            environment: InstructionEnvironmentForPreSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(environment)
        self._check_result_of_validate_pre_sds(result)
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(environment)
        self._check('result from validate/post-setup',
                    self.expectation.validation_post_setup,
                    result)
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      settings: InstructionSettings,
                      instruction: BeforeAssertPhaseInstruction) -> sh.SuccessOrHardError:
        return instruction.main(environment, settings, self.arrangement.os_services)

    def _check(self,
               component: str,
               assertion: Assertion,
               actual):
        assertion.apply(self.put,
                        actual,
                        asrt.MessageBuilder(component))
        return actual
