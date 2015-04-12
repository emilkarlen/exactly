__author__ = 'emil'

import pathlib
import tempfile
import unittest

from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import script_stmt_gen
from shelltest_test.execution.util.utils import Python3Language
from shelltest.exec_abs_syn.abs_syn_gen import \
    new_test_case_phase_for_python_commands, \
    new_test_case_phase_for_script_statements
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest import phases
from shelltest.execution import execution
from shelltest_test.execution.util import utils


class UnitTestCaseForPyLanguage:
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__()
        self.__previous_line_number = 0
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__test_case_execution = None
        self.__execution_directory_structure = None

    def execute(self):
        # ARRANGE #
        home_dir_path = pathlib.Path().resolve()
        settings = abs_syn_gen.GlobalEnvironmentForNamedPhase(str(home_dir_path))
        test_case = self._test_case(settings)
        python3_language = Python3Language()
        # ACT #
        if self.__dbg_do_not_delete_dir_structure:
            tmp_exec_dir_structure_root = tempfile.mkdtemp(prefix='shelltest-test-')
            print(tmp_exec_dir_structure_root)
            self.__act_with_existing_exec_dir_structure_root(tmp_exec_dir_structure_root,
                                                             python3_language,
                                                             test_case,
                                                             home_dir_path)
        else:
            with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_exec_dir_structure_root:
                self.__act_with_existing_exec_dir_structure_root(tmp_exec_dir_structure_root,
                                                                 python3_language,
                                                                 test_case,
                                                                 home_dir_path)

    def _phase_env_setup(self) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return self._phase_env_for_py_cmd_phase(phases.SETUP)

    def _phase_env_apply(self) -> abs_syn_gen.PhaseEnvironmentForScriptGeneration:
        raise NotImplementedError()

    def _phase_env_assert(self) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return self._phase_env_for_py_cmd_phase(phases.ASSERT)

    def _phase_env_cleanup(self, ) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return self._phase_env_for_py_cmd_phase(phases.CLEANUP)

    def _phase_env_for_py_cmd_phase(self, phase: phases.Phase) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        raise NotImplementedError()

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _assertions(self):
        """
        Implements all assertions after the test case has been executed.
        """
        raise NotImplementedError()

    @property
    def unittest_case(self) -> unittest.TestCase:
        return self.__unittest_case

    @property
    def test_case_execution(self) -> execution.TestCaseExecution:
        return self.__test_case_execution

    @property
    def eds(self) -> execution.ExecutionDirectoryStructure:
        return self.__execution_directory_structure

    def assert_is_regular_file_with_contents(self,
                                             path: pathlib.Path,
                                             expected_contents: str):
        """
        Helper for test cases that check the contents of files.
        """
        utils.assert_is_file_with_contents(self.unittest_case,
                                           path,
                                           expected_contents)

    def _test_case(self,
                   settings: abs_syn_gen.GlobalEnvironmentForNamedPhase) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(settings, [
            new_test_case_phase_for_python_commands(
                phases.SETUP,
                self._phase_env_setup()
            ),
            new_test_case_phase_for_script_statements(
                phases.ACT,
                self._phase_env_apply()),

            new_test_case_phase_for_python_commands(
                phases.ASSERT,
                self._phase_env_assert()
            ),
            new_test_case_phase_for_python_commands(
                phases.CLEANUP,
                self._phase_env_cleanup()
            ),
        ])

    def __act_with_existing_exec_dir_structure_root(self,
                                                    tmp_exec_dir_structure_root: str,
                                                    python3_language: script_stmt_gen.ScriptLanguage,
                                                    test_case: abs_syn_gen.TestCase,
                                                    home_dir_path: pathlib.Path):
        # ACT #
        test_case_execution = execution.TestCaseExecution(python3_language,
                                                          test_case,
                                                          tmp_exec_dir_structure_root,
                                                          home_dir_path)
        test_case_execution.write_and_execute()
        # ASSERT #
        self.__test_case_execution = test_case_execution
        self.__execution_directory_structure = test_case_execution.execution_directory_structure
        self._assertions()
