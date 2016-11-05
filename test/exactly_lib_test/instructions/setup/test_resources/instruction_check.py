import copy
import os
import pathlib
import tempfile
import unittest
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case import phase_identifier, sandbox_directory_structure
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import resolved_path_name
from exactly_lib_test.instructions.setup.test_resources import settings_check
from exactly_lib_test.instructions.test_resources import sh_check
from exactly_lib_test.instructions.test_resources import svh_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithEds
from exactly_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import sds_populator, sds_contents_check


class Arrangement(ArrangementWithEds):
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 os_services: OsServices = new_default(),
                 eds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder()):
        super().__init__(home_dir_contents, eds_contents_before_main, os_services)
        self.initial_settings_builder = initial_settings_builder


arrangement = Arrangement


class Expectation:
    def __init__(self,
                 pre_validation_result: svh_check.Assertion = svh_check.is_success(),
                 main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 main_side_effects_on_environment: settings_check.Assertion = settings_check.AnythingGoes(),
                 main_side_effects_on_files: sds_contents_check.Assertion = sds_contents_check.AnythingGoes(),
                 post_validation_result: svh_check.Assertion = svh_check.is_success(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.main_result = main_result
        self.main_side_effects_on_environment = main_side_effects_on_environment
        self.main_side_effects_on_files = main_side_effects_on_files
        self.post_validation_result = post_validation_result
        self.side_effects_check = side_effects_check


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: SingleInstructionParser,
               source: SingleInstructionParserSource,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: SingleInstructionParser,
          source: SingleInstructionParserSource,
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
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  SetupPhaseInstruction,
                                  'The instruction must be an instance of ' + str(SetupPhaseInstruction))
        assert isinstance(instruction, SetupPhaseInstruction)
        prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
        initial_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory(prefix=prefix + '-home-') as home_dir_name:
                home_dir_path = pathlib.Path(home_dir_name).resolve()
                self.arrangement.home_contents.write_to(home_dir_path)
                pre_validate_result = self._execute_pre_validate(home_dir_path, instruction)
                if not pre_validate_result.is_success:
                    return
                with tempfile.TemporaryDirectory(prefix=prefix + '-sds-') as eds_root_dir_name:
                    sds = sandbox_directory_structure.construct_at(resolved_path_name(eds_root_dir_name))
                    os.chdir(str(sds.act_dir))
                    global_environment_with_eds = i.InstructionEnvironmentForPostSdsStep(home_dir_path,
                                                                                         sds,
                                                                                         phase_identifier.SETUP.identifier)
                    main_result = self._execute_main(sds, global_environment_with_eds, instruction)
                    if not main_result.is_success:
                        return
                    self._execute_post_validate(global_environment_with_eds, instruction)
                    self.expectation.side_effects_check.apply(self.put, global_environment_with_eds.home_and_sds)
        finally:
            os.chdir(initial_cwd)

    def _execute_pre_validate(self,
                              home_dir_path: pathlib.Path,
                              instruction: SetupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        pre_validation_environment = InstructionEnvironmentForPreSdsStep(home_dir_path)
        pre_validate_result = instruction.validate_pre_sds(pre_validation_environment)
        self.put.assertIsInstance(pre_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'pre_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(pre_validate_result,
                                 'Result from pre_validate method cannot be None')
        self.expectation.pre_validation_result.apply(self.put, pre_validate_result)
        return pre_validate_result

    def _execute_main(self,
                      sds: SandboxDirectoryStructure,
                      global_environment_with_eds: i.InstructionEnvironmentForPostSdsStep,
                      instruction: SetupPhaseInstruction) -> sh.SuccessOrHardError:
        self.arrangement.eds_contents.apply(sds)
        settings_builder = self.arrangement.initial_settings_builder
        initial_settings_builder = copy.deepcopy(settings_builder)
        main_result = instruction.main(global_environment_with_eds,
                                       self.arrangement.os_services,
                                       settings_builder)
        self.put.assertIsInstance(main_result,
                                  sh.SuccessOrHardError,
                                  'main must return a ' + str(sh.SuccessOrHardError))
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.main_side_effects_on_environment.apply(self.put,
                                                                global_environment_with_eds,
                                                                initial_settings_builder,
                                                                settings_builder)
        self.expectation.main_side_effects_on_files.apply(self.put, sds)
        return main_result

    def _execute_post_validate(self,
                               global_environment_with_eds,
                               instruction: SetupPhaseInstruction, ) -> svh.SuccessOrValidationErrorOrHardError:
        post_validate_result = instruction.validate_post_setup(global_environment_with_eds)
        self.put.assertIsInstance(post_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'post_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(post_validate_result,
                                 'Result from post_validate method cannot be None')
        self.expectation.post_validation_result.apply(self.put, post_validate_result)
        return post_validate_result
