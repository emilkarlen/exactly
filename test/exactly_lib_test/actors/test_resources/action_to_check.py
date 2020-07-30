import os
import random
import unittest
from abc import ABC, abstractmethod
from typing import List

from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelHdsOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_utils.os_services import os_services_access
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.actors.test_resources import integration_check
from exactly_lib_test.actors.test_resources.integration_check import \
    Expectation, Arrangement, PostSdsExpectation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.instructions.multi_phase.change_dir import CwdSdsAssertion
from exactly_lib_test.test_case.actor.test_resources.act_phase_os_process_executor import \
    AtcOsProcessExecutorThatRaisesHardError
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRaisesHardError
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.ds_action import MkSubDirAndMakeItCurrentDirectory
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import SdsSubDirResolverWithRelSdsRoot
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestCaseSourceSetup:
    def __init__(self,
                 act_phase_instructions: List[ActPhaseInstruction],
                 home_act_dir_contents: DirContents = empty_dir_contents(),
                 ):
        self.home_act_dir_contents = home_act_dir_contents
        self.act_phase_instructions = act_phase_instructions


class Configuration(ABC):
    def __init__(self, sut: Actor):
        self.actor = sut

    @abstractmethod
    def program_that_exits_with_code(self,
                                     exit_code: int) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_copes_stdin_to_stdout(self) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_prints_to_stdout(self,
                                      string_to_print: str) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_prints_to_stderr(self,
                                      string_to_print: str) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_prints_cwd_to_stdout(self) -> TestCaseSourceSetup:
        pass

    @abstractmethod
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        pass


def suite_for_execution(setup: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite(tcc(setup) for tcc in
                              [TestStdoutIsConnectedToProgram,
                               TestStderrIsConnectedToProgram,
                               TestStdinAndStdoutAreConnectedToProgram,
                               TestExitCodeIsReturned,
                               TestEnvironmentVariablesAreAccessibleByProgram,
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
        setup = self.config.program_that_prints_to_stdout(stdout_output)
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
            ),
            Expectation(
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
        setup = self.config.program_that_prints_to_stderr(stderr_output)
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
            ),
            Expectation(
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
        setup = self.config.program_that_copes_stdin_to_stdout()
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
                stdin_contents=stdin_contents
            ),
            Expectation(
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                        stdout=asrt.equals(stdin_contents)
                    )
                )
            ),
        )


class TestExitCodeIsReturned(TestBase):
    def runTest(self):
        setup = self.config.program_that_exits_with_code(87)
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
            ),
            Expectation(
                execute=eh_assertions.is_exit_code(87)
            )
        )


class TestEnvironmentVariablesAreAccessibleByProgram(TestBase):
    def runTest(self):
        var_name = 'THIS_IS_A_TEST_VAR_23026509234'
        var_value = str(random.getrandbits(32))
        environ = dict(os.environ)
        environ[var_name] = var_value
        setup = self.config.program_that_prints_value_of_environment_variable_to_stdout(var_name)
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
                process_execution=ProcessExecutionArrangement(
                    process_execution_settings=ProcessExecutionSettings(
                        environ=environ
                    )
                )
            ),
            Expectation(
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

        def check_that_stdout_is_expected_cwd(sds: SandboxDirectoryStructure) -> PostSdsExpectation:
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

        setup = self.config.program_that_prints_cwd_to_stdout()
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
                post_sds_action=MkSubDirAndMakeItCurrentDirectory(
                    SdsSubDirResolverWithRelSdsRoot(RelSdsOptionType.REL_ACT, cwd_sub_dir_of_act)
                )
            ),
            Expectation(
                post_sds=check_that_stdout_is_expected_cwd
            )
        )


class TestTimeoutValueIsUsed(TestBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        setup = self.config.program_that_sleeps_at_least(5)
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
                process_execution=ProcessExecutionArrangement(
                    process_execution_settings=ProcessExecutionSettings(
                        timeout_in_seconds=1
                    )
                )
            ),
            Expectation(execute=eh_assertions.is_hard_error),
        )


class TestHardErrorFromExecutorIsDetected(TestBase):
    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def runTest(self):
        setup = self.config.program_that_exits_with_code(0)
        hard_error_message = 'the err msg'
        self._check(
            setup.act_phase_instructions,
            Arrangement(
                hds_contents=_hds_pop_of(setup),
                atc_process_executor=AtcOsProcessExecutorThatRaisesHardError(
                    asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                ),
                process_execution=ProcessExecutionArrangement(
                    os_services=os_services_access.new_for_cmd_exe(
                        CommandExecutorThatRaisesHardError(
                            asrt_text_doc.new_single_string_text_for_test(hard_error_message)
                        )
                    )
                )
            ),
            expectation=Expectation.hard_error_from_execute(
                error_message=asrt_text_doc.is_single_pre_formatted_text_that_equals(hard_error_message)
            )
        )


def _hds_pop_of(setup: TestCaseSourceSetup) -> HdsPopulator:
    return hds_populators.contents_in(
        RelHdsOptionType.REL_HDS_ACT,
        setup.home_act_dir_contents
    )
