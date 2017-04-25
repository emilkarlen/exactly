import copy
import os
import pathlib
import tempfile
import unittest
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.setup.test_resources import settings_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 os_services: OsServices = new_default(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder(),
                 home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 value_definitions: SymbolTable = None,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         home_contents=home_dir_contents,
                         sds_contents=sds_contents_before_main,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         home_or_sds_contents=home_or_sds_contents,
                         value_definitions=value_definitions)
        self.initial_settings_builder = initial_settings_builder


arrangement = Arrangement


class Expectation:
    def __init__(self,
                 pre_validation_result: va.ValueAssertion = svh_check.is_success(),
                 main_result: va.ValueAssertion = sh_check.is_success(),
                 main_side_effects_on_environment: settings_check.Assertion = settings_check.AnythingGoes(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 post_validation_result: va.ValueAssertion = svh_check.is_success(),
                 side_effects_check: va.ValueAssertion = va.anything_goes(),
                 source: va.ValueAssertion = va.anything_goes(),
                 value_definition_usages: va.ValueAssertion = va.anything_goes(),
                 value_definitions_after_main: va.ValueAssertion = va.anything_goes(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.main_result = main_result
        self.main_side_effects_on_environment = main_side_effects_on_environment
        self.main_side_effects_on_files = main_side_effects_on_files
        self.post_validation_result = post_validation_result
        self.side_effects_check = side_effects_check
        self.source = source
        self.value_definition_usages = value_definition_usages
        self.value_definitions_after_main = value_definitions_after_main


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
        self.expectation.value_definition_usages.apply_with_message(self.put, instruction.value_usages(),
                                                                    'value-definition-usages')
        prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
        initial_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(prefix=prefix + '-home-') as home_dir_name:
                home_dir_path = pathlib.Path(home_dir_name).resolve()
                self.arrangement.home_contents.write_to(home_dir_path)
                environment = InstructionEnvironmentForPreSdsStep(home_dir_path,
                                                                  self.arrangement.process_execution_settings.environ,
                                                                  value_definitions=self.arrangement.value_definitions)
                pre_validate_result = self._execute_pre_validate(environment, instruction)
                if not pre_validate_result.is_success:
                    return
                with tempfile.TemporaryDirectory(prefix=prefix + '-sds-') as sds_root_dir_name:
                    sds = sandbox_directory_structure.construct_at(resolved_path_name(sds_root_dir_name))
                    os.chdir(str(sds.act_dir))
                    instruction_environment = i.InstructionEnvironmentForPostSdsStep(
                        environment.home_directory,
                        environment.environ,
                        sds,
                        phase_identifier.SETUP.identifier,
                        timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                        value_definitions=self.arrangement.value_definitions)
                    home_and_sds = HomeAndSds(home_dir_path, sds)
                    path_resolving_environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds,
                                                                                      self.arrangement.value_definitions)
                    self.arrangement.pre_contents_population_action.apply(path_resolving_environment)
                    self.arrangement.sds_contents.apply(sds)
                    self.arrangement.home_or_sds_contents.write_to(home_and_sds)
                    self.arrangement.post_sds_population_action.apply(path_resolving_environment)
                    main_result = self._execute_main(sds, instruction_environment, instruction)
                    if not main_result.is_success:
                        return
                    self.expectation.value_definitions_after_main.apply_with_message(
                        self.put,
                        instruction_environment.value_definitions,
                        'value_definitions_after_main')
                    self._execute_post_validate(instruction_environment, instruction)
                    self.expectation.side_effects_check.apply(self.put, instruction_environment.home_and_sds)
        finally:
            os.chdir(initial_cwd)

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
        initial_settings_builder = copy.deepcopy(settings_builder)
        main_result = instruction.main(instruction_environment,
                                       self.arrangement.os_services,
                                       settings_builder)
        self.put.assertIsInstance(main_result,
                                  sh.SuccessOrHardError,
                                  'main must return a ' + str(sh.SuccessOrHardError))
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.main_side_effects_on_environment.apply(self.put,
                                                                instruction_environment,
                                                                initial_settings_builder,
                                                                settings_builder)
        self.expectation.main_side_effects_on_files.apply(self.put, sds)
        return main_result

    def _execute_post_validate(self,
                               global_environment_with_sds,
                               instruction: SetupPhaseInstruction, ) -> svh.SuccessOrValidationErrorOrHardError:
        post_validate_result = instruction.validate_post_setup(global_environment_with_sds)
        self.put.assertIsInstance(post_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'post_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(post_validate_result,
                                 'Result from post_validate method cannot be None')
        self.expectation.post_validation_result.apply(self.put, post_validate_result)
        return post_validate_result
