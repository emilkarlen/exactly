import os
import shutil
import pathlib
import types
import unittest

from shelltest.test_case.abs_syn_gen import TestCase
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest.execution.partial_execution import execute_test_case_in_execution_directory, PartialExecutor
from shelltest.document import model
from shelltest.document import line_source
from shelltest.script_language import python3
from shelltest.test_case import abs_syn_gen
from shelltest import phases
from shelltest_test.execution.util import utils, instruction_adapter
from shelltest_test.execution.util.test_case_generation import TestCaseGeneratorBase


class UnitTestCaseForPy3Language:
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
        test_case = self._test_case()
        # ACT #
        test_case_execution = execute_test_case_in_execution_directory(
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

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
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
    def test_case_execution(self) -> PartialExecutor:
        return self.__test_case_execution

    @property
    def eds(self) -> ExecutionDirectoryStructure:
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

    def _test_case(self) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(
            model.PhaseContents(tuple(self._anonymous_phase())),
            model.PhaseContents(tuple(self._setup_phase())),
            model.PhaseContents(tuple(self._act_phase())),
            model.PhaseContents(tuple(self._assert_phase())),
            model.PhaseContents(tuple(self._cleanup_phase())))

    def _anonymous_phase(self) -> list:
        return []

    def _setup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_setup(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.SETUP)]

    def _act_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return []

    def _assert_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_assert(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.ASSERT)]

    def _cleanup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_cleanup(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.CLEANUP)]

    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        """
        :rtype list[InternalInstruction]
        """
        return []


class Result(tuple):
    """
    Result of test execution.
    """

    def __new__(cls,
                home_dir_path: pathlib.Path,
                partial_executor: PartialExecutor,
                execution_directory_structure: ExecutionDirectoryStructure):
        return tuple.__new__(cls, (home_dir_path,
                                   partial_executor,
                                   execution_directory_structure))

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self[0]

    @property
    def partial_executor(self) -> PartialExecutor:
        return self[1]

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self[2]


def py3_test(unittest_case: unittest.TestCase,
             test_case: TestCase,
             assertions: types.FunctionType,
             dbg_do_not_delete_dir_structure=False):
    # SETUP #
    home_dir_path = pathlib.Path().resolve()
    # ACT #
    test_case_execution = execute_test_case_in_execution_directory(
        python3.Python3ScriptFileManager(),
        python3.new_script_source_writer(),
        test_case,
        home_dir_path,
        'shelltest-test-',
        True)
    # ASSERT #
    eds = test_case_execution.execution_directory_structure
    result = Result(home_dir_path,
                    test_case_execution,
                    eds)

    assertions(unittest_case,
               result)
    # CLEANUP #
    os.chdir(str(home_dir_path))
    if not dbg_do_not_delete_dir_structure:
        shutil.rmtree(str(eds.root_dir))
    else:
        print(str(eds.root_dir))


class TestCaseWithCommonDefaultForSetupAssertCleanup(TestCaseGeneratorBase):
    def _setup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_setup(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.SETUP)]

    def _assert_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_assert(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.ASSERT)]

    def _cleanup_phase(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return [self._next_instruction_line(instruction_adapter.as_cleanup(instr))
                for instr in self._default_instructions_for_setup_assert_cleanup(phases.CLEANUP)]

    def _default_instructions_for_setup_assert_cleanup(self, phase: phases.Phase) -> list:
        """
        :rtype list[InternalInstruction]
        """
        return []
