import os
import shutil
import pathlib
import types
import unittest

from shellcheck_lib.test_case.test_case_doc import TestCase
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.partial_execution import execute_test_case_in_execution_directory, PartialExecutor
from shellcheck_lib.act_phase_setups import python3
from shellcheck_lib.execution import phases
from shellcheck_lib_test.execution.util import instruction_adapter
from shellcheck_lib_test.execution.util.test_case_generation import TestCaseGeneratorBase


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
        python3.new_script_handling(),
        test_case,
        home_dir_path,
        'shellcheck-test-',
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
