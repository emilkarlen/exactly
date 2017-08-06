import os
import pathlib
import shutil
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from .basic import Result


class Arrangement:
    def __init__(self,
                 test_case: partial_execution.TestCase,
                 act_phase_handling: ActPhaseHandling,
                 home_case_dir_path: pathlib.Path() = pathlib.Path(),
                 home_act_dir_path: pathlib.Path() = pathlib.Path(),
                 initial_setup_settings: setup.SetupSettingsBuilder = setup.default_settings()):
        self.home_case_dir_path = home_case_dir_path
        self.home_act_dir_path = home_act_dir_path
        self.test_case = test_case
        self.act_phase_handling = act_phase_handling
        self.initial_setup_settings = initial_setup_settings


class Expectation:
    def __init__(self,
                 assertion_on_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 partial_result: asrt.ValueAssertion = asrt.anything_goes()):
        self.partial_result = partial_result
        self.assertion_on_sds = assertion_on_sds


def execute_and_check(put: unittest.TestCase,
                      arrangement: Arrangement,
                      expectation: Expectation):
    with preserved_cwd():
        home_case_dir_path = arrangement.home_case_dir_path.resolve()
        home_act_dir_path = arrangement.home_act_dir_path.resolve()
        hds = HomeDirectoryStructure(case_dir=home_case_dir_path,
                                     act_dir=home_act_dir_path)
        partial_result = partial_execution.execute(
            arrangement.act_phase_handling,
            arrangement.test_case,
            partial_execution.Configuration(ACT_PHASE_OS_PROCESS_EXECUTOR,
                                            hds,
                                            dict(os.environ)),
            arrangement.initial_setup_settings,
            program_info.PROGRAM_NAME + '-test-',
            is_keep_execution_directory_root=True)

        expectation.partial_result.apply_with_message(put,
                                                      partial_result,
                                                      'partial_result')
        result = Result(hds, partial_result)
        expectation.assertion_on_sds.apply_with_message(put,
                                                        result.partial_result.sds,
                                                        'Sandbox Directory Structure')
    # CLEANUP #
    if result is not None and result.sds is not None:
        if result.sds.root_dir.exists():
            shutil.rmtree(str(result.sds.root_dir))
