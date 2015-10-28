import copy
import os
import pathlib
import tempfile
from time import strftime, localtime
import unittest

from shellcheck_lib.document.parse import SectionElementParser
from shellcheck_lib.execution import execution_directory_structure
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction
from shellcheck_lib.test_case.os_services import new_default, OsServices
from shellcheck_lib_test.util import file_structure
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources import eds_populator


class Flow:
    def __init__(self,
                 sut: ActPhaseSetup,
                 os_services: OsServices=new_default(),
                 home_dir_contents: file_structure.DirContents=file_structure.DirContents([]),
                 eds_contents: eds_populator.EdsPopulator=eds_populator.Empty(),
                 expected_validation_result: svh_check.Assertion=svh_check.is_success()
                 ):
        self.sut = sut
        self.home_dir_contents = home_dir_contents
        self.eds_contents = eds_contents
        self.os_services = os_services
        self.expected_validation_result = expected_validation_result


class TestCaseBase(unittest.TestCase):
    def _check(self,
               check: Flow,
               act_phase_source: str):
        execute(self,
                check,
                act_phase_source)


def execute(put: unittest.TestCase,
            setup: Flow,
            act_phase_source: str):
    instructions = _parse(setup.sut.parser, source)
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


def _execute_main(eds, global_environment_with_eds,
                  instruction: SetupPhaseInstruction,
                  put,
                  setup: Flow) -> sh.SuccessOrHardError:
    setup.eds_contents.apply(eds)
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


def _parse(parser: SectionElementParser,
           act_phase_source: str) -> list:
    raise NotImplementedError()
