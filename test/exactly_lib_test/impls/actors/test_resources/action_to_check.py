import os
import random
import unittest
from abc import ABC, abstractmethod
from typing import List, ContextManager, Mapping, Optional, Sequence

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import RelSdsOptionType, RelHdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.impls.actors.test_resources import integration_check
from exactly_lib_test.impls.actors.test_resources.integration_check import \
    Expectation, Arrangement, PostSdsExpectation, arrangement_w_tcds, AtcExeInputArr
from exactly_lib_test.impls.instructions.multi_phase.change_dir import CwdSdsAssertion
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.tcfs.test_resources.dir_populator import HdsPopulator
from exactly_lib_test.tcfs.test_resources.ds_action import MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsSubDirResolverWithRelSdsRoot
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRaisesHardError
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


class TestCaseSourceSetup:
    def __init__(self,
                 act_phase_instructions: List[ActPhaseInstruction],
                 home_act_dir_contents: DirContents = empty_dir_contents(),
                 environ: Optional[Mapping[str, str]] = None,
                 symbols: Optional[SymbolTable] = None,
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 ):
        self.symbols = symbol_table_from_none_or_value(symbols)
        self.home_act_dir_contents = home_act_dir_contents
        self.act_phase_instructions = act_phase_instructions
        self.environ = environ
        self.symbol_usages = symbol_usages


class Configuration(ABC):
    def __init__(self, sut: Actor):
        self.actor = sut

    @abstractmethod
    def program_that_exits_with_code(self,
                                     exit_code: int) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_copes_stdin_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str
                                                                    ) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_prints_cwd_to_stdout(self) -> ContextManager[TestCaseSourceSetup]:
        pass

    @abstractmethod
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> ContextManager[TestCaseSourceSetup]:
        pass


def suite_for_execution(setup: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(setup) for tcc in
                              [TestStdoutIsConnectedToProgram,
                               TestStderrIsConnectedToProgram,
                               TestStdinAndStdoutAreConnectedToProgram,
                               TestExitCodeIsReturned,
                               TestEnvVarsOfAtAreThoseFromActExecutionInput,
                               TestCwdOfAtcIsCurrentDirCurrentDirIsNotChangedByTheActor,
                               TestTimeoutValueIsUsed,
                               TestHardErrorFromExecutorIsDetected,
                               ])


class TestExecuteBase(unittest.TestCase):
    def __init__(self, actor: Actor):
        super().__init__()
        self.actor = actor


class TestBase(TestExecuteBase):
    def __init__(self, conf: Configuration):
        super().__init__(conf.actor)
        self.config = conf

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.config))

    def _check(self,
               instructions: List[ActPhaseInstruction],
               arrangement: Arrangement,
               expectation: Expectation,
               ):
        integration_check.check_execution(self,
                                          self.config.actor,
                                          instructions,
                                          arrangement,
                                          expectation)


class TestStdoutIsConnectedToProgram(TestBase):
    def runTest(self):
        stdout_output = 'output on stdout'
        with self.config.program_that_prints_to_stdout(stdout_output) as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    act_exe_input=AtcExeInputArr(
                        environ=setup.environ
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    post_sds=PostSdsExpectation.constant(
                        sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                            stdout=asrt.equals(stdout_output + '\n')
                        )
                    )
                ),
            )


class TestStderrIsConnectedToProgram(TestBase):
    def runTest(self):
        stderr_output = 'output on stderr'
        with self.config.program_that_prints_to_stderr(stderr_output) as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    act_exe_input=AtcExeInputArr(
                        environ=setup.environ
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    post_sds=PostSdsExpectation.constant(
                        sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                            stderr=asrt.equals(stderr_output + '\n')
                        )
                    )
                ),
            )


class TestStdinAndStdoutAreConnectedToProgram(TestBase):
    def runTest(self):
        stdin_contents = 'contents of stdin'
        with self.config.program_that_copes_stdin_to_stdout() as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    act_exe_input=AtcExeInputArr(
                        stdin_contents=stdin_contents,
                        environ=setup.environ,
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    post_sds=PostSdsExpectation.constant(
                        sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                            stdout=asrt.equals(stdin_contents)
                        )
                    )
                ),
            )


class TestExitCodeIsReturned(TestBase):
    def runTest(self):
        with self.config.program_that_exits_with_code(87) as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    act_exe_input=AtcExeInputArr(
                        environ=setup.environ
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    execute=eh_assertions.is_exit_code(87),
                )
            )


class TestEnvVarsOfAtAreThoseFromActExecutionInput(TestBase):
    def runTest(self):
        var_name = 'This_Is_A_Test_Var_23026509234'
        var_value = str(random.getrandbits(32))
        with self.config.program_that_prints_value_of_environment_variable_to_stdout(var_name) as setup:
            environ = (
                dict(os.environ)
                if setup.environ is None
                else
                setup.environ
            )
            environ[var_name] = var_value
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    process_execution=ProcessExecutionArrangement(
                        process_execution_settings=proc_exe_env_for_test()
                    ),
                    act_exe_input=AtcExeInputArr(
                        environ=environ,
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    post_sds=PostSdsExpectation.constant(
                        sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                            stdout=asrt.equals(var_value + '\n')
                        )
                    )
                ),
            )


class TestCwdOfAtcIsCurrentDirCurrentDirIsNotChangedByTheActor(TestBase):
    def runTest(self):
        cwd_sub_dir_of_act = 'the-sub-dir-that-should-be-cwd'

        def check_that_stdout_is_expected_cwd(sds: SandboxDs) -> PostSdsExpectation:
            return PostSdsExpectation(
                sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                    stdout=asrt.equals(
                        str(sds.act_dir / cwd_sub_dir_of_act) + '\n'
                    )
                ),
                side_effects_on_files_after_execute=CwdSdsAssertion(
                    RelSdsOptionType.REL_ACT,
                    cwd_sub_dir_of_act,
                )
            )

        with self.config.program_that_prints_cwd_to_stdout() as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    post_sds_action=MkSubDirAndMakeItCurrentDirectory(
                        SdsSubDirResolverWithRelSdsRoot(RelSdsOptionType.REL_ACT, cwd_sub_dir_of_act)
                    ),
                    act_exe_input=AtcExeInputArr(
                        environ=setup.environ
                    ),
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    post_sds=check_that_stdout_is_expected_cwd,
                )
            )


class TestTimeoutValueIsUsed(TestBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        with self.config.program_that_sleeps_at_least(5) as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    process_execution=ProcessExecutionArrangement(
                        process_execution_settings=proc_exe_env_for_test(
                            timeout_in_seconds=1,
                            environ=setup.environ,
                        )
                    )
                ),
                Expectation(
                    symbol_usages=setup.symbol_usages,
                    execute=eh_assertions.is_hard_error,
                ),
            )


class TestHardErrorFromExecutorIsDetected(TestBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        hard_error_message = 'the err msg'
        with self.config.program_that_exits_with_code(0) as setup:
            self._check(
                setup.act_phase_instructions,
                arrangement_w_tcds(
                    symbol_table=setup.symbols,
                    hds_contents=_hds_pop_of(setup),
                    process_execution=ProcessExecutionArrangement(
                        os_services=os_services_access.new_for_cmd_exe(
                            CommandExecutorThatRaisesHardError(
                                asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                            )
                        ),
                        process_execution_settings=proc_exe_env_for_test(
                            environ=setup.environ
                        ),
                    )
                ),
                expectation=Expectation.hard_error_from_execute(
                    symbol_usages=setup.symbol_usages,
                    error_message=asrt_text_doc.is_single_pre_formatted_text_that_equals(hard_error_message),
                )
            )


def _hds_pop_of(setup: TestCaseSourceSetup) -> HdsPopulator:
    return hds_populators.contents_in(
        RelHdsOptionType.REL_HDS_ACT,
        setup.home_act_dir_contents
    )
