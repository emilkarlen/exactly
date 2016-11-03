import os
import pathlib
import shutil
import types
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution
from exactly_lib.execution.act_phase import ActPhaseHandling
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.execution.phases import PhaseEnum
from exactly_lib.execution.result import PartialResult
from exactly_lib.test_case.phases import setup
from exactly_lib.util.functional import Composition
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, cleanup_phase_instruction_that, \
    act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import TestCaseGeneratorBase, \
    instruction_line_constructor


class Result(tuple):
    """
    Result of test execution.
    """

    def __new__(cls,
                home_dir_path: pathlib.Path,
                partial_result: PartialResult):
        return tuple.__new__(cls, (home_dir_path,
                                   partial_result))

    @property
    def home_dir_path(self) -> pathlib.Path:
        return self[0]

    @property
    def partial_result(self) -> PartialResult:
        return self[1]

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.partial_result.execution_directory_structure


class TestCaseGeneratorForPartialExecutionBase(TestCaseGeneratorBase):
    """
    Base class for generation of Test Cases for partial execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    @property
    def test_case(self) -> partial_execution.TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> partial_execution.TestCase:
        return build(self)


def build(tc: TestCaseGeneratorBase) -> partial_execution.TestCase:
    return partial_execution.TestCase(
        tc.setup_phase(),
        tc.act_phase(),
        tc.before_assert_phase(),
        tc.assert_phase(),
        tc.cleanup_phase()
    )


class TestCaseWithCommonDefaultInstructions(TestCaseGeneratorForPartialExecutionBase):
    def __init__(self):
        super().__init__()
        self.instruction_line_constructor = instruction_line_constructor()

    def _setup_phase(self) -> list:
        return self._phase_elements(lambda main: setup_phase_instruction_that(main=main),
                                    PhaseEnum.SETUP)

    def _act_phase(self) -> list:
        return self._phase_elements(lambda main: act_phase_instruction_with_source(),
                                    PhaseEnum.ACT)

    def _before_assert_phase(self) -> list:
        return self._phase_elements(lambda main: before_assert_phase_instruction_that(main=main),
                                    PhaseEnum.BEFORE_ASSERT)

    def _assert_phase(self) -> list:
        return self._phase_elements(lambda main: assert_phase_instruction_that(main=main),
                                    PhaseEnum.ASSERT)

    def _cleanup_phase(self) -> list:
        return self._phase_elements(lambda main: cleanup_phase_instruction_that(main=main),
                                    PhaseEnum.CLEANUP)

    def _phase_elements(self,
                        instruction_in_phase_adapter: types.FunctionType,
                        phase: PhaseEnum) -> list:
        return list(map(Composition(self.instruction_line_constructor,
                                    instruction_in_phase_adapter),
                        self._default_instructions(phase)))

    def _default_instructions(self, phase: PhaseEnum) -> list:
        """
        :rtype Function that can serve as main to PHASE_phase_instruction_that.
        """
        return []


def dummy_act_phase_handling() -> ActPhaseHandling:
    return ActPhaseHandling(ActSourceAndExecutorConstructorThatRunsConstantActions())


def test(unittest_case: unittest.TestCase,
         test_case: partial_execution.TestCase,
         act_phase_handling: ActPhaseHandling,
         assertions: types.FunctionType,
         is_keep_execution_directory_root: bool = True,
         dbg_do_not_delete_dir_structure=False):
    result = _execute(test_case,
                      act_phase_handling,
                      is_keep_execution_directory_root=is_keep_execution_directory_root)

    assertions(unittest_case,
               result)
    # CLEANUP #
    os.chdir(str(result.home_dir_path))
    if not dbg_do_not_delete_dir_structure:
        if result.execution_directory_structure.root_dir.exists():
            shutil.rmtree(str(result.execution_directory_structure.root_dir))
    else:
        print(str(result.execution_directory_structure.root_dir))


def _execute(test_case: partial_execution.TestCase,
             act_phase_handling: ActPhaseHandling,
             is_keep_execution_directory_root: bool = True) -> Result:
    home_dir_path = pathlib.Path().resolve()
    partial_result = partial_execution.execute(
        act_phase_handling,
        test_case,
        home_dir_path,
        setup.default_settings(),
        program_info.PROGRAM_NAME + '-test-',
        is_keep_execution_directory_root)
    return Result(home_dir_path,
                  partial_result)
