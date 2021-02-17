import pathlib
import shutil
import unittest
from typing import Callable, Optional, Mapping, Dict

from exactly_lib.execution.configuration import ExecutionConfiguration
from exactly_lib.execution.partial_execution import execution as sut
from exactly_lib.execution.partial_execution.configuration import ConfPhaseValues, TestCase
from exactly_lib.execution.partial_execution.result import PartialExeResult
from exactly_lib.execution.partial_execution.setup_settings_handler import StandardSetupSettingsHandler
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.environ import DefaultEnvironGetter
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.file_utils.std import StdOutputFiles
from exactly_lib.util.functional import Composition
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.partial_execution.test_resources import result_assertions as asrt_pr
from exactly_lib_test.execution.test_resources import sandbox_root_name_resolver
from exactly_lib_test.execution.test_resources.instruction_test_resources import setup_phase_instruction_that, \
    before_assert_phase_instruction_that, assert_phase_instruction_that, cleanup_phase_instruction_that, \
    act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import TestCaseGeneratorBase, \
    instruction_line_constructor
from exactly_lib_test.test_case.actor.test_resources.actors import dummy_actor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Result(tuple):
    """
    Result of test execution.
    """

    def __new__(cls,
                hds: HomeDs,
                partial_result: PartialExeResult):
        return tuple.__new__(cls, (hds,
                                   partial_result))

    @property
    def hds(self) -> HomeDs:
        return self[0]

    @property
    def sds(self) -> SandboxDs:
        return self.partial_result.sds

    @property
    def partial_result(self) -> PartialExeResult:
        return self[1]


def result_matches(hds: Assertion[HomeDs] = asrt.anything_goes(),
                   sds: Assertion[SandboxDs] = asrt.anything_goes(),
                   partial_result: Assertion[PartialExeResult] = asrt.anything_goes(),
                   ) -> Assertion[Result]:
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


def result_is_pass(hds: Assertion[HomeDs] = asrt.anything_goes(),
                   sds: Assertion[SandboxDs] = asrt.anything_goes(),
                   ) -> Assertion[Result]:
    return result_matches(
        hds=hds,
        sds=sds,
        partial_result=asrt_pr.is_pass()
    )


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
                        instruction_in_phase_adapter: Callable,
                        phase: PhaseEnum) -> list:
        return list(map(Composition(self.instruction_line_constructor,
                                    instruction_in_phase_adapter),
                        self._default_instructions(phase)))

    def _default_instructions(self, phase: PhaseEnum) -> list:
        """
        :rtype Function that can serve as main to PHASE_phase_instruction_that.
        """
        return []


def _default_environ_getter() -> Dict[str, str]:
    return {}


class Arrangement:
    def __init__(self,
                 actor: Actor = dummy_actor(),
                 hds: HomeDs = HomeDs(pathlib.Path().resolve(),
                                      pathlib.Path().resolve()),
                 environ: Optional[Mapping[str, str]] = None,
                 default_environ_getter: DefaultEnvironGetter = _default_environ_getter,
                 timeout_in_seconds: int = None,
                 predefined_symbols: SymbolTable = None,
                 exe_atc_and_skip_assertions: Optional[StdOutputFiles] = None,
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 mem_buff_size: int = 2 ** 10,
                 ):
        self.actor = actor
        self.os_services = os_services
        self.hds = hds
        self.environ = environ
        self.default_environ_getter = default_environ_getter
        self.timeout_in_seconds = timeout_in_seconds
        self.predefined_symbols_or_none = predefined_symbols
        self.exe_atc_and_skip_assertions = exe_atc_and_skip_assertions
        self.mem_buff_size = mem_buff_size


def test(put: unittest.TestCase,
         test_case: TestCase,
         actor: Actor,
         assertions: Callable[[unittest.TestCase, Result], None],
         is_keep_sandbox: bool = True):
    with preserved_cwd():
        result = _execute(test_case,
                          Arrangement(actor=actor),
                          is_keep_sandbox=is_keep_sandbox)

        assertions(put,
                   result)
    # CLEANUP #
    if result.sds.root_dir.exists():
        shutil.rmtree(str(result.sds.root_dir))


def test__va(put: unittest.TestCase,
             test_case: TestCase,
             arrangement: Arrangement,
             assertions_on_result: Assertion[Result],
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
        shutil.rmtree(str(result.sds.root_dir),
                      ignore_errors=True)


def _execute(test_case: TestCase,
             arrangement: Arrangement,
             is_keep_sandbox: bool = True) -> Result:
    partial_result = sut.execute(
        test_case,
        ExecutionConfiguration(arrangement.default_environ_getter,
                               arrangement.environ,
                               arrangement.os_services,
                               sandbox_root_name_resolver.for_test(),
                               arrangement.mem_buff_size,
                               arrangement.predefined_symbols_or_none,
                               exe_atc_and_skip_assertions=arrangement.exe_atc_and_skip_assertions),
        ConfPhaseValues(NameAndValue('the actor', arrangement.actor),
                        arrangement.hds,
                        timeout_in_seconds=arrangement.timeout_in_seconds),
        StandardSetupSettingsHandler.new_from_environ,
        is_keep_sandbox)
    return Result(arrangement.hds,
                  partial_result)
