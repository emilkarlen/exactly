import copy
import os
import pathlib
import tempfile
import unittest
from time import strftime, localtime

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.test_case.os_services import new_default, OsServices
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.instructions.setup.test_resources import settings_check
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.utils import SideEffectsCheck
from shellcheck_lib_test.util import file_structure


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 os_services: OsServices = new_default(),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder(),
                 expected_pre_validation_result: svh_check.Assertion = svh_check.is_success(),
                 expected_main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 expected_main_side_effects_on_environment: settings_check.Assertion = settings_check.AnythingGoes(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 expected_post_validation_result: svh_check.Assertion = svh_check.is_success(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.os_services = os_services
        self.expected_pre_validation_result = expected_pre_validation_result
        self.eds_contents_before_main = eds_contents_before_main
        self.initial_settings_builder = initial_settings_builder
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_environment = expected_main_side_effects_on_environment
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files
        self.expected_post_validation_result = expected_post_validation_result
        self.side_effects_check = side_effects_check


class Arrangement:
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 os_services: OsServices = new_default(),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 initial_settings_builder: SetupSettingsBuilder = SetupSettingsBuilder(),
                 ):
        self.home_dir_contents = home_dir_contents
        self.os_services = os_services
        self.eds_contents_before_main = eds_contents_before_main
        self.initial_settings_builder = initial_settings_builder


class Expectation:
    def __init__(self,
                 pre_validation_result: svh_check.Assertion = svh_check.is_success(),
                 main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 main_side_effects_on_environment: settings_check.Assertion = settings_check.AnythingGoes(),
                 main_side_effects_on_files: eds_contents_check.Assertion = eds_contents_check.AnythingGoes(),
                 post_validation_result: svh_check.Assertion = svh_check.is_success(),
                 side_effects_check: SideEffectsCheck = SideEffectsCheck(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.main_result = main_result
        self.main_side_effects_on_environment = main_side_effects_on_environment
        self.main_side_effects_on_files = main_side_effects_on_files
        self.post_validation_result = post_validation_result
        self.side_effects_check = side_effects_check


def flow(parser: SingleInstructionParser,
         arrangement: Arrangement,
         expectation: Expectation) -> Flow:
    return Flow(parser,
                home_dir_contents=arrangement.home_dir_contents,
                os_services=arrangement.os_services,
                eds_contents_before_main=arrangement.eds_contents_before_main,
                initial_settings_builder=arrangement.initial_settings_builder,
                expected_pre_validation_result=expectation.pre_validation_result,
                expected_main_result=expectation.main_result,
                expected_main_side_effects_on_environment=expectation.main_side_effects_on_environment,
                expected_main_side_effects_on_files=expectation.main_side_effects_on_files,
                expected_post_validation_result=expectation.post_validation_result,
                side_effects_check=expectation.side_effects_check,
                )


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               source: SingleInstructionParserSource):
        execute(self, check, source)

    def _check2(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource,
                arrangement: Arrangement,
                expectation: Expectation):
        self._check(flow(parser, arrangement, expectation), source)


def execute(put: unittest.TestCase,
            setup: Flow,
            source: SingleInstructionParserSource):
    instruction = setup.parser.apply(source)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         SetupPhaseInstruction,
                         'The instruction must be an instance of ' + str(SetupPhaseInstruction))
    assert isinstance(instruction, SetupPhaseInstruction)
    prefix = strftime("shellcheck-test-%Y-%m-%d-%H-%M-%S", localtime())
    initial_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir_name:
            home_dir_path = pathlib.Path(home_dir_name)
            setup.home_dir_contents.write_to(home_dir_path)
            pre_validate_result = _execute_pre_validate(home_dir_path, instruction, put, setup)
            if not pre_validate_result.is_success:
                return
            with tempfile.TemporaryDirectory(prefix=prefix + "-eds-") as eds_root_dir_name:
                eds = execution_directory_structure.construct_at(eds_root_dir_name)
                os.chdir(str(eds.act_dir))
                global_environment_with_eds = i.GlobalEnvironmentForPostEdsPhase(home_dir_path,
                                                                                 eds)
                main_result = _execute_main(eds, global_environment_with_eds, instruction, put, setup)
                if not main_result.is_success:
                    return
                _execute_post_validate(global_environment_with_eds, instruction, put, setup)
                setup.side_effects_check.apply(put, global_environment_with_eds.home_and_eds)
    finally:
        os.chdir(initial_cwd)


def _execute_pre_validate(home_dir_path,
                          instruction: SetupPhaseInstruction,
                          put, setup) -> svh.SuccessOrValidationErrorOrHardError:
    pre_validation_environment = GlobalEnvironmentForPreEdsStep(home_dir_path)
    pre_validate_result = instruction.pre_validate(pre_validation_environment)
    put.assertIsInstance(pre_validate_result,
                         svh.SuccessOrValidationErrorOrHardError,
                         'pre_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
    put.assertIsNotNone(pre_validate_result,
                        'Result from pre_validate method cannot be None')
    setup.expected_pre_validation_result.apply(put, pre_validate_result)
    return pre_validate_result


def _execute_main(eds,
                  global_environment_with_eds: i.GlobalEnvironmentForPostEdsPhase,
                  instruction: SetupPhaseInstruction,
                  put,
                  setup: Flow) -> sh.SuccessOrHardError:
    setup.eds_contents_before_main.apply(eds)
    settings_builder = setup.initial_settings_builder
    initial_settings_builder = copy.deepcopy(settings_builder)
    main_result = instruction.main(setup.os_services,
                                   global_environment_with_eds,
                                   settings_builder)
    put.assertIsInstance(main_result,
                         sh.SuccessOrHardError,
                         'main must return a ' + str(sh.SuccessOrHardError))
    put.assertIsNotNone(main_result,
                        'Result from main method cannot be None')
    setup.expected_main_result.apply(put, main_result)
    setup.expected_main_side_effects_on_environment.apply(put,
                                                          global_environment_with_eds,
                                                          initial_settings_builder,
                                                          settings_builder)
    setup.expected_main_side_effects_on_files.apply(put, eds)
    return main_result


def _execute_post_validate(global_environment_with_eds,
                           instruction: SetupPhaseInstruction,
                           put, setup) -> svh.SuccessOrValidationErrorOrHardError:
    post_validate_result = instruction.post_validate(global_environment_with_eds)
    put.assertIsInstance(post_validate_result,
                         svh.SuccessOrValidationErrorOrHardError,
                         'post_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
    put.assertIsNotNone(post_validate_result,
                        'Result from post_validate method cannot be None')
    setup.expected_post_validation_result.apply(put, post_validate_result)
    return post_validate_result
