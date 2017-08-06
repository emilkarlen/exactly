import os
import pathlib
import shutil
import types
import unittest

from exactly_lib import program_info
from exactly_lib.execution import partial_execution
from exactly_lib.execution.result import PartialResult
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.functional import Composition
from exactly_lib_test.execution.test_resources.act_source_executor import \
    ActSourceAndExecutorConstructorThatRunsConstantActions
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, cleanup_phase_instruction_that, \
    act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import TestCaseGeneratorBase, \
    instruction_line_constructor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Result(tuple):
    """
    Result of test execution.
    """

    def __new__(cls,
                hds: HomeDirectoryStructure,
                partial_result: PartialResult):
        return tuple.__new__(cls, (hds,
                                   partial_result))

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self[0]

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self.partial_result.sds

    @property
    def partial_result(self) -> PartialResult:
        return self[1]


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
         is_keep_execution_directory_root: bool = True):
    with preserved_cwd():
        result = _execute(test_case,
                          act_phase_handling,
                          is_keep_execution_directory_root=is_keep_execution_directory_root)

        assertions(unittest_case,
                   result)
    # CLEANUP #
    if result.sds.root_dir.exists():
        shutil.rmtree(str(result.sds.root_dir))


def test__va(unittest_case: unittest.TestCase,
             test_case: partial_execution.TestCase,
             act_phase_handling: ActPhaseHandling,
             assertions_on_result: asrt.ValueAssertion):
    with preserved_cwd():
        result = _execute(test_case,
                          act_phase_handling,
                          is_keep_execution_directory_root=False)

        assertions_on_result.apply(unittest_case,
                                   result,
                                   asrt.MessageBuilder('Result'))
    # CLEANUP #
    if result.sds.root_dir.exists():
        shutil.rmtree(str(result.sds.root_dir))


def _execute(test_case: partial_execution.TestCase,
             act_phase_handling: ActPhaseHandling,
             is_keep_execution_directory_root: bool = True) -> Result:
    home_case_dir_path = pathlib.Path().resolve()
    home_act_dir_path = pathlib.Path().resolve()
    hds = HomeDirectoryStructure(case_dir=home_case_dir_path,
                                 act_dir=home_act_dir_path)
    partial_result = partial_execution.execute(
        act_phase_handling,
        test_case,
        partial_execution.Configuration(ACT_PHASE_OS_PROCESS_EXECUTOR,
                                        hds,
                                        dict(os.environ)),
        setup.default_settings(),
        program_info.PROGRAM_NAME + '-test-',
        is_keep_execution_directory_root)
    return Result(hds,
                  partial_result)
