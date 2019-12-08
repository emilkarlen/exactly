import os
import unittest

from exactly_lib.execution import phase_step
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SettingsBuilderAssertionModel(tuple):
    def __new__(cls,
                actual: SetupSettingsBuilder,
                environment: common.InstructionEnvironmentForPostSdsStep,
                ):
        return tuple.__new__(cls, (actual, environment))

    @property
    def actual(self) -> SetupSettingsBuilder:
        return self[0]

    @property
    def environment(self) -> common.InstructionEnvironmentForPostSdsStep:
        return self[1]


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder(),
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_hds_contents=non_hds_contents,
                         tcds_contents=tcds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols,
                         fs_location_info=fs_location_info,
                         )
        self.initial_settings_builder = initial_settings_builder


class Expectation:
    """
    Expectation on properties of the execution of an instruction.
    
    Default settings: successful steps execution and NO symbol usages.
    """

    def __init__(self,
                 pre_validation_result: ValueAssertion = svh_assertions.is_success(),
                 main_result: ValueAssertion = sh_assertions.is_success(),
                 post_validation_result: ValueAssertion = svh_assertions.is_success(),
                 symbol_usages: ValueAssertion = asrt.is_empty_sequence,
                 main_side_effects_on_sds: ValueAssertion = asrt.anything_goes(),
                 main_side_effects_on_tcds: ValueAssertion = asrt.anything_goes(),
                 settings_builder: ValueAssertion = asrt.anything_goes(),
                 source: ValueAssertion = asrt.anything_goes(),
                 symbols_after_main: ValueAssertion = asrt.anything_goes(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.post_validation_result = post_validation_result
        self.settings_builder = settings_builder
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main


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


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: InstructionParser,
                source: ParseSource):
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  SetupPhaseInstruction,
                                  'The instruction must be an instance of ' + str(SetupPhaseInstruction))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, SetupPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
                                                          'symbol-usages after parse')
        self.expectation.symbol_usages.apply_with_message(self.put, instruction.symbol_usages(),
                                                          'symbol-usages')

        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:

            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            with preserved_cwd():
                os.chdir(str(path_resolving_environment.hds.case_dir))

                environment = InstructionEnvironmentForPreSdsStep(path_resolving_environment.hds,
                                                                  self.arrangement.process_execution_settings.environ,
                                                                  symbols=self.arrangement.symbols)
                pre_validate_result = self._execute_pre_validate(environment, instruction)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  instruction.symbol_usages(),
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if not pre_validate_result.is_success:
                    return

            instruction_environment = i.InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                path_resolving_environment.sds,
                phase_identifier.SETUP.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)

            tcds = path_resolving_environment.tcds
            sds = tcds.sds

            main_result = self._execute_main(instruction_environment, instruction)

            self.expectation.main_side_effects_on_sds.apply(self.put, sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
            if not main_result.is_success:
                return
            self.expectation.symbols_after_main.apply_with_message(
                self.put,
                instruction_environment.symbols,
                'symbols_after_main')
            self._execute_post_validate(instruction_environment, instruction)
            self.expectation.main_side_effects_on_tcds.apply(self.put,
                                                             instruction_environment.tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            self.expectation.settings_builder.apply_with_message(
                self.put,
                SettingsBuilderAssertionModel(self.arrangement.initial_settings_builder,
                                              instruction_environment),
                'settings builder'
            )

    def _execute_pre_validate(self,
                              environment: InstructionEnvironmentForPreSdsStep,
                              instruction: SetupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        pre_validate_result = instruction.validate_pre_sds(environment)
        self.put.assertIsInstance(pre_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'pre_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(pre_validate_result,
                                 'Result from pre_validate method cannot be None')
        self.expectation.pre_validation_result.apply(self.put, pre_validate_result)
        return pre_validate_result

    def _execute_main(self,
                      instruction_environment: i.InstructionEnvironmentForPostSdsStep,
                      instruction: SetupPhaseInstruction) -> sh.SuccessOrHardError:
        settings_builder = self.arrangement.initial_settings_builder
        main_result = instruction.main(instruction_environment,
                                       self.arrangement.os_services,
                                       settings_builder)
        self.put.assertIsInstance(main_result,
                                  sh.SuccessOrHardError,
                                  'main must return a ' + str(sh.SuccessOrHardError))
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        return main_result

    def _execute_post_validate(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               instruction: SetupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        post_validate_result = instruction.validate_post_setup(environment)
        self.put.assertIsInstance(post_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'post_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(post_validate_result,
                                 'Result from post_validate method cannot be None')
        self.expectation.post_validation_result.apply(self.put, post_validate_result)
        return post_validate_result
