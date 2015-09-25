import copy
import os
import pathlib
import tempfile
from time import strftime, localtime
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.test_case.instruction.common import GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.instruction.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder
from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.instructions import utils
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import sh_check
from shellcheck_lib_test.instructions.test_resources import eds_populator
from shellcheck_lib_test.instructions.test_resources import eds_contents_check
from shellcheck_lib_test.instructions.setup.test_resources import settings_check


class Flow:
    def __init__(self,
                 parser: SingleInstructionParser,
                 home_dir_contents: file_structure.DirContents=file_structure.DirContents([]),
                 expected_pre_validation_result: svh_check.Assertion=svh_check.AnythingGoes(),
                 eds_contents_before_main: eds_populator.EdsPopulator=eds_populator.Empty(),
                 initial_settings_builder: SetupSettingsBuilder=SetupSettingsBuilder(),
                 expected_main_result: sh_check.Assertion=sh_check.AnythingGoes(),
                 expected_main_side_effects_on_environment: settings_check.Assertion=settings_check.AnythingGoes(),
                 expected_main_side_effects_on_files: eds_contents_check.Assertion=eds_contents_check.AnythingGoes(),
                 expected_post_validation_result: svh_check.Assertion=svh_check.AnythingGoes()
                 ):
        self.parser = parser
        self.home_dir_contents = home_dir_contents
        self.expected_pre_validation_result = expected_pre_validation_result
        self.eds_contents_before_main = eds_contents_before_main
        self.initial_settings_builder = initial_settings_builder
        self.expected_main_result = expected_main_result
        self.expected_main_side_effects_on_environment = expected_main_side_effects_on_environment
        self.expected_main_side_effects_on_files = expected_main_side_effects_on_files
        self.expected_post_validation_result = expected_post_validation_result


def execute(put: unittest.TestCase,
            setup: Flow,
            source: utils.SingleInstructionParserSource):
    instruction = setup.parser.apply(source.line_sequence, source.instruction_argument)
    put.assertIsNotNone(instruction,
                        'Result from parser cannot be None')
    put.assertIsInstance(instruction,
                         SetupPhaseInstruction,
                         'The instruction must be an instance of ' + str(SetupPhaseInstruction))
    assert isinstance(instruction, SetupPhaseInstruction)
    # home-dir
    prefix = strftime("shellcheck-test-%Y-%m-%d-%H-%M-%S", localtime())
    initial_cwd = os.getcwd()
    try:
        with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir_name:
            home_dir_path = pathlib.Path(home_dir_name)
            setup.home_dir_contents.write_to(home_dir_path)
            # pre-validation
            pre_validation_environment = GlobalEnvironmentForPreEdsStep(home_dir_path)
            pre_validate_result = instruction.pre_validate(pre_validation_environment)
            put.assertIsNotNone(pre_validate_result,
                                'Result from pre_validate method cannot be None')
            setup.expected_pre_validation_result.apply(put, pre_validate_result)
            with tempfile.TemporaryDirectory(prefix=prefix + "-eds-") as eds_root_dir_name:
                eds = execution_directory_structure.construct_at(eds_root_dir_name)
                # main
                os.chdir(str(eds.test_root_dir))
                setup.eds_contents_before_main.apply(eds)
                global_environment_with_eds = i.GlobalEnvironmentForPostEdsPhase(home_dir_path,
                                                                                 eds)
                settings_builder = setup.initial_settings_builder
                # TODO : check på settings
                initial_settings_builder = copy.deepcopy(settings_builder)
                main_result = instruction.main(global_environment_with_eds,
                                               settings_builder)
                put.assertIsNotNone(main_result,
                                    'Result from main method cannot be None')
                setup.expected_main_result.apply(put, main_result)
                setup.expected_main_side_effects_on_environment.apply(initial_settings_builder,
                                                                      settings_builder)
                setup.expected_main_side_effects_on_files.apply(put, eds)
                # post-validation
                post_validate_result = instruction.post_validate(global_environment_with_eds)
                put.assertIsNotNone(post_validate_result,
                                    'Result from post_validate method cannot be None')
                setup.expected_post_validation_result.apply(put, post_validate_result)
    finally:
        os.chdir(initial_cwd)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               source: utils.SingleInstructionParserSource):
        execute(self, check, source)
