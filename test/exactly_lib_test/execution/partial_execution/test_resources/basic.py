import pathlib
import shutil
import types
import unittest
from typing import Callable, Optional

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.os_services import DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases import setup
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib.util.functional import Composition
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.execution.test_resources.act_source_and_executor_constructors import \
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
                partial_result: PartialExeResult):
        return tuple.__new__(cls, (hds,
                                   partial_result))

    @property
    def hds(self) -> HomeDirectoryStructure:
        return self[0]

    @property
    def sds(self) -> SandboxDirectoryStructure:
        return self.partial_result.sds

    @property
    def partial_result(self) -> PartialExeResult:
        return self[1]


def result_assertion(hds: asrt.ValueAssertion[HomeDirectoryStructure] = asrt.anything_goes(),
                     sds: asrt.ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
                     partial_result: asrt.ValueAssertion[PartialExeResult] = asrt.anything_goes(),
                     ) -> asrt.ValueAssertion[Result]:
    return asrt.and_([
        asrt.sub_component('hds',
                           Result.hds.fget,
                           hds),
        asrt.sub_component('sds',
                           Result.sds.fget,
                           sds),
        asrt.sub_component('partial_result',
                           Result.partial_result.fget,
                           partial_result),
    ])


class TestCaseGeneratorForPartialExecutionBase(TestCaseGeneratorBase):
    """
    Base class for generation of Test Cases for partial execution.
    """

    def __init__(self):
        super().__init__()
        self.__test_case = None

    @property
    def test_case(self) -> TestCase:
        if self.__test_case is None:
            self.__test_case = self._generate()
        return self.__test_case

    def _generate(self) -> TestCase:
        return build(self)


def build(tc: TestCaseGeneratorBase) -> TestCase:
    return TestCase(
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


class Arrangement:
    def __init__(self,
                 act_phase_handling: ActPhaseHandling = dummy_act_phase_handling(),
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor = DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                 hds: HomeDirectoryStructure = HomeDirectoryStructure(pathlib.Path().resolve(),
                                                                      pathlib.Path().resolve()),
                 environ: dict = None,
                 timeout_in_seconds: int = None,
                 predefined_symbols: SymbolTable = None,
                 exe_atc_and_skip_assertions: Optional[StdOutputFiles] = None):
        self.act_phase_handling = act_phase_handling
        self.act_phase_os_process_executor = act_phase_os_process_executor
        self.hds = hds
        self.environ = environ
        self.timeout_in_seconds = timeout_in_seconds
        self.predefined_symbols_or_none = predefined_symbols
        self.exe_atc_and_skip_assertions = exe_atc_and_skip_assertions


def test(put: unittest.TestCase,
         test_case: TestCase,
         act_phase_handling: ActPhaseHandling,
         assertions: Callable[[unittest.TestCase, Result], None],
         is_keep_sandbox: bool = True):
    with preserved_cwd():
        result = _execute(test_case,
                          Arrangement(act_phase_handling=act_phase_handling),
                          is_keep_sandbox=is_keep_sandbox)

        assertions(put,
                   result)
    # CLEANUP #
    if result.sds.root_dir.exists():
        shutil.rmtree(str(result.sds.root_dir))


def test__va(put: unittest.TestCase,
             test_case: TestCase,
             arrangement: Arrangement,
             assertions_on_result: asrt.ValueAssertion[Result],
             is_keep_sandbox_during_assertions: bool = False):
    with preserved_cwd():
        result = _execute(test_case,
                          arrangement,
                          is_keep_sandbox=is_keep_sandbox_during_assertions)

        assertions_on_result.apply(put,
                                   result,
                                   asrt.MessageBuilder('Result'))
    # CLEANUP #
    if result.sds.root_dir.exists():
        shutil.rmtree(str(result.sds.root_dir))


def _execute(test_case: TestCase,
             arrangement: Arrangement,
             is_keep_sandbox: bool = True) -> Result:
    environ = arrangement.environ
    if environ is None:
        environ = {}
    partial_result = sut.execute(
        test_case,
        ExecutionConfiguration(environ,
                               arrangement.act_phase_os_process_executor,
                               sandbox_root_name_resolver.for_test(),
                               arrangement.predefined_symbols_or_none,
                               exe_atc_and_skip_assertions=arrangement.exe_atc_and_skip_assertions),
        ConfPhaseValues(arrangement.act_phase_handling,
                        arrangement.hds,
                        timeout_in_seconds=arrangement.timeout_in_seconds),
        setup.default_settings(),
        is_keep_sandbox)
    return Result(arrangement.hds,
                  partial_result)
