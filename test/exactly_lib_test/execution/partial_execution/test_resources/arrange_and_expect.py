import os
import pathlib
import shutil
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.test_case.phases import setup
from exactly_lib_test.test_resources.file_structure_utils import preserved_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from .basic import Result


class Arrangement:
    def __init__(self,
                 test_case: partial_execution.TestCase,
                 act_phase_handling: ActPhaseHandling,
                 home_dir_path: pathlib.Path() = pathlib.Path(),
                 initial_setup_settings: setup.SetupSettingsBuilder = setup.default_settings()):
        self.home_dir_path = home_dir_path
        self.test_case = test_case
        self.act_phase_handling = act_phase_handling
        self.initial_setup_settings = initial_setup_settings


class Expectation:
    def __init__(self,
                 assertion_on_sds: va.ValueAssertion = va.anything_goes()):
        self.assertion_on_sds = assertion_on_sds


def execute_and_check(put: unittest.TestCase,
                      arrangement: Arrangement,
                      expectation: Expectation):
    with preserved_cwd():
        home_dir_path = arrangement.home_dir_path.resolve()
        partial_result = partial_execution.execute(
            arrangement.act_phase_handling,
            arrangement.test_case,
            partial_execution.Configuration(home_dir_path),
            arrangement.initial_setup_settings,
            program_info.PROGRAM_NAME + '-test-',
            is_keep_execution_directory_root=True)
        result = Result(home_dir_path, partial_result)
        expectation.assertion_on_sds.apply(put,
                                           result.partial_result.execution_directory_structure,
                                           va.MessageBuilder('Sandbox Directory Structure'))
        # CLEANUP #
        os.chdir(str(result.home_dir_path))
        if result.execution_directory_structure.root_dir.exists():
            shutil.rmtree(str(result.execution_directory_structure.root_dir))
