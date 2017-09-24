import os
import os
import unittest
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_home_contents: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder(),
                 symbols: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_home_contents=non_home_contents,
                         home_or_sds_contents=home_or_sds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols)
        self.initial_settings_builder = initial_settings_builder


class Expectation:
    """
    Expectation on properties of the execution of an instruction.
    
    Default settings: successful steps execution and NO symbol usages.
    """

    def __init__(self,
                 pre_validation_result: asrt.ValueAssertion = svh_assertions.is_success(),
                 main_result: asrt.ValueAssertion = sh_assertions.is_success(),
                 post_validation_result: asrt.ValueAssertion = svh_assertions.is_success(),
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 main_side_effects_on_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 main_side_effects_on_home_and_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 settings_builder: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 symbols_after_main: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.post_validation_result = post_validation_result
        self.settings_builder = settings_builder
        self.main_side_effects_on_home_and_sds = main_side_effects_on_home_and_sds
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
        instruction = parser.parse(source)
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
        prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
        with preserved_cwd():
            with home_directory_structure(prefix=prefix + '-home',
                                          contents=self.arrangement.hds_contents,
                                          ) as hds:
                environment = InstructionEnvironmentForPreSdsStep(hds,
                                                                  self.arrangement.process_execution_settings.environ,
                                                                  symbols=self.arrangement.symbols)
                pre_validate_result = self._execute_pre_validate(environment, instruction)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  instruction.symbol_usages(),
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if not pre_validate_result.is_success:
                    return
                with sandbox_directory_structure(prefix=prefix + '-sds-') as sds:
                    os.chdir(str(sds.act_dir))
                    instruction_environment = i.InstructionEnvironmentForPostSdsStep(
                        environment.hds,
                        environment.environ,
                        sds,
                        phase_identifier.SETUP.identifier,
                        timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                        symbols=self.arrangement.symbols)
                    home_and_sds = HomeAndSds(hds, sds)
                    path_resolving_environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds,
                                                                                      self.arrangement.symbols)
                    self.arrangement.pre_contents_population_action.apply(path_resolving_environment)
                    self.arrangement.sds_contents.populate_sds(sds)
                    self.arrangement.non_home_contents.populate_non_home(sds)
                    self.arrangement.home_or_sds_contents.populate_home_or_sds(home_and_sds)
                    self.arrangement.post_sds_population_action.apply(path_resolving_environment)
                    main_result = self._execute_main(sds, instruction_environment, instruction)
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
                    self.expectation.main_side_effects_on_home_and_sds.apply(self.put,
                                                                             instruction_environment.home_and_sds)
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
                      sds: SandboxDirectoryStructure,
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
        self.expectation.main_side_effects_on_sds.apply(self.put, sds)
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
