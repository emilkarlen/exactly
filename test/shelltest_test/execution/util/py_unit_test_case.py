from shelltest.script_language.python3 import Python3Language

__author__ = 'emil'

import os
import shutil
import pathlib
import unittest

from shelltest.phase_instr import model
from shelltest.phase_instr import line_source
from shelltest.script_language import python3
from shelltest.exec_abs_syn.abs_syn_gen import \
    new_test_case_phase_for_python_commands, \
    new_test_case_phase_for_script_statements
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.exec_abs_syn import instructions
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
        settings = instructions.GlobalEnvironmentForNamedPhase(str(home_dir_path))
        test_case = self._test_case(settings)
        python3_language = Python3Language()
        # ACT #
        test_case_execution = execution.execute_test_case_in_execution_directory(python3_language,
                                                                                 test_case,
                                                                                 home_dir_path,
                                                                                 'shelltest-test-',
                                                                                 True)

        # ASSERT #
        self.__test_case_execution = test_case_execution
        self.__execution_directory_structure = test_case_execution.execution_directory_structure
        self._assertions()
        # CLEANUP #
        os.chdir(str(home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure:
            shutil.rmtree(str(self.__execution_directory_structure.root_dir))
        else:
            print(str(test_case_execution.execution_directory_structure.root_dir))

    def _phase_env_setup(self) -> abs_syn_gen.PhaseEnvironmentForPythonCommands:
        return self._phase_env_for_py_cmd_phase(phases.SETUP)

    def _phase_env_act(self) -> instructions.PhaseEnvironmentForScriptGeneration:
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
                   settings: instructions.GlobalEnvironmentForNamedPhase) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(settings, [
            new_test_case_phase_for_python_commands(
                phases.SETUP,
                self._phase_env_setup()
            ),
            new_test_case_phase_for_script_statements(
                phases.ACT,
                self._phase_env_act()),

            new_test_case_phase_for_python_commands(
                phases.ASSERT,
                self._phase_env_assert()
            ),
            new_test_case_phase_for_python_commands(
                phases.CLEANUP,
                self._phase_env_cleanup()
            ),
        ])


class UnitTestCaseForPyLanguage2:
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
        settings = instructions.GlobalEnvironmentForNamedPhase(home_dir_path)
        test_case = self._test_case()
        # ACT #
        test_case_execution = execution.execute_test_case_in_execution_directory2(
            python3.Python3ScriptFileManager(),
            python3.new_script_source_writer(),
            test_case,
            home_dir_path,
            'shelltest-test-',
            True)

        # ASSERT #
        self.__test_case_execution = test_case_execution
        self.__execution_directory_structure = test_case_execution.execution_directory_structure
        self._assertions()
        # CLEANUP #
        os.chdir(str(home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure:
            shutil.rmtree(str(self.__execution_directory_structure.root_dir))
        else:
            print(str(test_case_execution.execution_directory_structure.root_dir))

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _next_instruction_line(self, instruction: model.InstructionExecutor) -> model.PhaseContentElement:
        return model.new_instruction_element(
            self._next_line(),
            instruction)

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

    def _test_case(self) -> abs_syn_gen.TestCase2:
        return abs_syn_gen.TestCase2(
            model.PhaseContents(tuple(self._anonymous_phase())),
            model.PhaseContents(tuple(self._setup_phase())),
            model.PhaseContents(tuple(self._act_phase())),
            model.PhaseContents(tuple(self._assert_phase())),
            model.PhaseContents(tuple(self._cleanup_phase())))

    def _anonymous_phase(self) -> list:
        return []

    def _setup_phase(self) -> list:
        return []

    def _act_phase(self) -> list:
        return []

    def _assert_phase(self) -> list:
        return []

    def _cleanup_phase(self) -> list:
        return []

