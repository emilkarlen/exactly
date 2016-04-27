import os
import pathlib
import shutil
import types
import unittest

from exactly_lib import program_info
from exactly_lib.act_phase_setups import python3
from exactly_lib.default.program_modes.test_case.processing import script_handling_for_setup
from exactly_lib.execution import partial_execution
from exactly_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from exactly_lib.execution.phases import PhaseEnum
from exactly_lib.execution.result import PartialResult
from exactly_lib.util.functional import Composition
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, cleanup_phase_instruction_that, \
    act_phase_instruction_that
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

    @property
    def configuration(self) -> partial_execution.Configuration:
        return partial_execution.Configuration(self.home_dir_path,
                                               str(self.execution_directory_structure.act_dir))


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
        return self._phase_elements(lambda main: act_phase_instruction_that(main=main),
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


def py3_test(unittest_case: unittest.TestCase,
             test_case: partial_execution.TestCase,
             assertions: types.FunctionType,
             is_keep_execution_directory_root: bool = True,
             dbg_do_not_delete_dir_structure=False):
    result = _execute(test_case,
                      script_handling_for_setup(python3.new_act_phase_setup()),
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


class PartialExecutionTestCaseBase:
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 dbg_do_not_delete_dir_structure=False,
                 script_handling: partial_execution.ScriptHandling = None):
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__initial_home_dir_path = None
        self.__script_handling = script_handling
        self.__result = None
        if self.__script_handling is None:
            self.__script_handling = script_handling_for_setup(python3.new_act_phase_setup())

    def execute(self):
        # SETUP #
        self.__initial_home_dir_path = pathlib.Path().resolve()
        # ACT #
        self.__result = _execute(self._test_case(),
                                 self.__script_handling)

        # ASSERT #
        self._assertions()
        # CLEANUP #
        os.chdir(str(self.__initial_home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

    def _test_case(self) -> partial_execution.TestCase:
        raise NotImplementedError()

    def _assertions(self):
        raise NotImplementedError()

    @property
    def utc(self) -> unittest.TestCase:
        return self.__unittest_case

    @property
    def initial_home_dir_path(self) -> pathlib.Path:
        return self.__initial_home_dir_path

    @property
    def result(self) -> Result:
        return self.__result

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.result.execution_directory_structure


def _execute(test_case: partial_execution.TestCase,
             script_handling: partial_execution.ScriptHandling,
             is_keep_execution_directory_root: bool = True) -> Result:
    home_dir_path = pathlib.Path().resolve()
    partial_result = partial_execution.execute(
            script_handling,
            test_case,
            home_dir_path,
        program_info.PROGRAM_NAME + '-test-',
            is_keep_execution_directory_root)
    return Result(home_dir_path,
                  partial_result)
