import os
import pathlib
import shutil
import subprocess
import tempfile

from exactly_lib.execution import environment_variables
from exactly_lib.execution import phase_step
from exactly_lib.execution import phase_step_executors
from exactly_lib.execution import phases
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.execution.phase_step_execution import ElementHeaderExecutor
from exactly_lib.execution.single_instruction_executor import ControlledInstructionExecutor
from exactly_lib.section_document.model import SectionContents
from exactly_lib.test_case.os_services import new_default, OsServices
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act.phase_setup import PhaseEnvironmentForScriptGeneration, ActSourceExecutor, \
    SourceSetup, ActSourceBuilder
from exactly_lib.test_case.phases.cleanup import PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.setup import SetupSettingsBuilder, StdinSettings
from exactly_lib.util import line_source
from exactly_lib.util.file_utils import write_new_text_file, resolved_path_name
from exactly_lib.util.std import StdOutputFiles, StdFiles
from . import phase_step_execution
from . import result
from .execution_directory_structure import construct_at, ExecutionDirectoryStructure, stdin_contents_file
from .result import PartialResult, PartialResultStatus, new_partial_result_pass, PhaseFailureInfo


class Configuration(tuple):
    def __new__(cls,
                home_dir: pathlib.Path,
                execution_directory_root_name_prefix: str):
        return tuple.__new__(cls, (home_dir, execution_directory_root_name_prefix))

    @property
    def home_dir(self) -> pathlib.Path:
        return self[0]

    @property
    def execution_directory_root_name_prefix(self) -> str:
        return self[1]


class TestCase(tuple):
    def __new__(cls,
                setup_phase: SectionContents,
                act_phase: SectionContents,
                before_assert_phase: SectionContents,
                assert_phase: SectionContents,
                cleanup_phase: SectionContents):
        return tuple.__new__(cls, (setup_phase,
                                   act_phase,
                                   before_assert_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def setup_phase(self) -> SectionContents:
        return self[0]

    @property
    def act_phase(self) -> SectionContents:
        return self[1]

    @property
    def before_assert_phase(self) -> SectionContents:
        return self[2]

    @property
    def assert_phase(self) -> SectionContents:
        return self[3]

    @property
    def cleanup_phase(self) -> SectionContents:
        return self[4]


class _StepExecutionResult:
    def __init__(self):
        self.__script_source = None
        self.__stdin_settings = None

    @property
    def script_source(self) -> str:
        return self.__script_source

    @script_source.setter
    def script_source(self, x: str):
        self.__script_source = x

    @property
    def has_custom_stdin(self) -> bool:
        return self.__stdin_settings.file_name is not None or \
               self.__stdin_settings.contents is not None

    @property
    def stdin_settings(self) -> StdinSettings:
        return self.__stdin_settings

    @stdin_settings.setter
    def stdin_settings(self, x: StdinSettings):
        self.__stdin_settings = x


class ActPhaseHandling:
    def __init__(self,
                 source_builder: ActSourceBuilder,
                 executor: ActSourceExecutor):
        self.source_builder = source_builder
        self.executor = executor


def execute(act_phase_handling: ActPhaseHandling,
            test_case: TestCase,
            home_dir_path: pathlib.Path,
            execution_directory_root_name_prefix: str,
            is_keep_execution_directory_root: bool) -> PartialResult:
    """
    Takes care of construction of the Execution Directory Structure, including
    the root directory, and executes a given Test Case in this directory.

    Preserves Current Working Directory.

    Perhaps the test case should be executed in a sub process, so that
    Environment Variables and Current Working Directory of the process that executes
    the main program is not modified.

    The responsibility of this method is not the most natural!!
    Please refactor if a more natural responsibility evolves!
    """
    cwd_before = None
    ret_val = None
    try:
        cwd_before = os.getcwd()
        configuration = Configuration(home_dir_path,
                                      execution_directory_root_name_prefix)

        test_case_execution = PartialExecutor(configuration,
                                              act_phase_handling,
                                              test_case)
        ret_val = test_case_execution.execute()
        return ret_val
    finally:
        if cwd_before is not None:
            os.chdir(cwd_before)
        if not is_keep_execution_directory_root:
            if ret_val is not None and ret_val.has_execution_directory_structure:
                shutil.rmtree(str(ret_val.execution_directory_structure.root_dir))


def construct_eds(execution_directory_root_name_prefix: str) -> ExecutionDirectoryStructure:
    eds_structure_root = tempfile.mkdtemp(prefix=execution_directory_root_name_prefix)
    return construct_at(resolved_path_name(eds_structure_root))


class PartialExecutor:
    def __init__(self,
                 configuration: Configuration,
                 act_phase_handling: ActPhaseHandling,
                 test_case: TestCase):
        self.__execution_directory_structure = None
        self.__global_environment_pre_eds = GlobalEnvironmentForPreEdsStep(configuration.home_dir)
        self.__act_phase_handling = act_phase_handling
        self.__test_case = test_case
        self.__configuration = configuration
        self.___step_execution_result = _StepExecutionResult()
        self.__source_setup = None

    def execute(self) -> PartialResult:
        # TODO Köra det här i sub-process?
        # Tror det behövs för att undvika att sätta omgivningen mm, o därmed
        # påverka huvudprocessen.
        self.__set_pre_eds_environment_variables()
        res = self.__setup__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__act__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__before_assert__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__assert__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        res = self.__cleanup__validate_pre_eds()
        if res.status is not PartialResultStatus.PASS:
            return res
        self.__construct_and_set_eds()
        os_services = new_default()
        self.__set_cwd_to_act_dir()
        self.__set_post_eds_environment_variables()
        res = self.__setup__main(os_services)
        previous_phase = PreviousPhase.SETUP
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__setup__validate_post_setup()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__act__validate_post_setup()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__before_assert__validate_post_setup()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__assert__validate_post_setup()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__act__script_generation()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__act__script_validate()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        res = self.__act__script_execute()
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(previous_phase, os_services)
            return res
        self.__set_assert_environment_variables()
        res = self.__before_assert__main(os_services)
        if res.status is not PartialResultStatus.PASS:
            self.__cleanup_main(PreviousPhase.BEFORE_ASSERT, os_services)
            return res
        ret_val = self.__assert__main(os_services)
        res = self.__cleanup_main(PreviousPhase.ASSERT, os_services)
        if res.is_failure:
            ret_val = res
        return ret_val

    @property
    def _eds(self) -> ExecutionDirectoryStructure:
        return self.__execution_directory_structure

    @property
    def configuration(self) -> Configuration:
        return self.__configuration

    def _store_exit_code(self, exitcode: int):
        with open(str(self._eds.result.exitcode_file), 'w') as f:
            f.write(str(exitcode))

    def __setup__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.SETUP__VALIDATE_PRE_EDS,
                                                           phase_step_executors.SetupValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.setup_phase)

    def __act__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ACT__VALIDATE_PRE_EDS,
                                                           phase_step_executors.ActValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.act_phase)

    def __before_assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS,
            phase_step_executors.BeforeAssertValidatePreEdsExecutor(self.__global_environment_pre_eds),
            self.__test_case.before_assert_phase)

    def __assert__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.ASSERT__VALIDATE_PRE_EDS,
                                                           phase_step_executors.AssertValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.assert_phase)

    def __cleanup__validate_pre_eds(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(phase_step.CLEANUP__VALIDATE_PRE_EDS,
                                                           phase_step_executors.CleanupValidatePreEdsExecutor(
                                                               self.__global_environment_pre_eds),
                                                           self.__test_case.cleanup_phase)

    def __setup__main(self, os_services: OsServices) -> PartialResult:
        setup_settings_builder = SetupSettingsBuilder()
        ret_val = self.__run_internal_instructions_phase_step(phase_step.SETUP__MAIN,
                                                              phase_step_executors.SetupMainExecutor(
                                                                  os_services,
                                                                  self.__post_eds_environment(phases.SETUP),
                                                                  setup_settings_builder),
                                                              self.__test_case.setup_phase)
        self.___step_execution_result.stdin_settings = setup_settings_builder.stdin

        return ret_val

    def __setup__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.SETUP__VALIDATE_POST_SETUP,
            phase_step_executors.SetupValidatePostSetupExecutor(
                self.__post_eds_environment(phases.SETUP)),
            self.__test_case.setup_phase)

    def __act__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.ACT__VALIDATE_POST_SETUP,
            phase_step_executors.ActValidatePostSetupExecutor(
                self.__post_eds_environment(phases.ACT)),
            self.__test_case.act_phase)

    def __act__script_generation(self) -> PartialResult:
        """
        Accumulates the script source by executing all instructions, and adding
        comments from the test case file.

        :param act_environment: Post-condition: Contains the accumulated script source.
        """
        script_builder = self.__act_phase_handling.source_builder
        environment = PhaseEnvironmentForScriptGeneration(script_builder)
        ret_val = phase_step_execution.execute_phase(
            self.__test_case.act_phase,
            _ActCommentHeaderExecutor(environment),
            _ActInstructionHeaderExecutor(environment),
            phase_step_executors.ActMainExecutor(self.__post_eds_environment(phases.ACT),
                                                 environment),
            phase_step.ACT__MAIN,
            self._eds)
        self.___step_execution_result.script_source = script_builder.build()
        return ret_val

    def __act__script_validate(self) -> PartialResult:
        the_phase_step = phase_step.ACT__SCRIPT_VALIDATE
        try:
            res = self.__act_phase_handling.executor.validate(self.configuration.home_dir,
                                                              self.__act_phase_handling.source_builder)
            if res.is_success:
                return new_partial_result_pass(self.__execution_directory_structure)
            else:
                return PartialResult(PartialResultStatus(res.status.value),
                                     self.__execution_directory_structure,
                                     PhaseFailureInfo(the_phase_step,
                                                      result.new_failure_details_from_message(res.failure_message)))
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 self.__execution_directory_structure,
                                 PhaseFailureInfo(the_phase_step,
                                                  result.new_failure_details_from_exception(ex)))

    def __before_assert__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.BeforeAssertValidatePostSetupExecutor(
                self.__post_eds_environment(phases.BEFORE_ASSERT)),
            self.__test_case.before_assert_phase)

    def __assert__validate_post_setup(self) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.ASSERT__VALIDATE_POST_SETUP,
            phase_step_executors.AssertValidatePostSetupExecutor(
                self.__post_eds_environment(phases.ASSERT)),
            self.__test_case.assert_phase)

    def __assert__main(self, phase_env) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.ASSERT__MAIN,
            phase_step_executors.AssertMainExecutor(
                self.__post_eds_environment(phases.ASSERT),
                phase_env),
            self.__test_case.assert_phase)

    def __cleanup_main(self, previous_phase: PreviousPhase, os_services) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.CLEANUP__MAIN,
            phase_step_executors.CleanupMainExecutor(
                self.__post_eds_environment(phases.CLEANUP),
                previous_phase,
                os_services),
            self.__test_case.cleanup_phase)

    def __before_assert__main(self, os_services) -> PartialResult:
        return self.__run_internal_instructions_phase_step(
            phase_step.BEFORE_ASSERT__MAIN,
            phase_step_executors.BeforeAssertMainExecutor(
                self.__post_eds_environment(phases.BEFORE_ASSERT),
                os_services),
            self.__test_case.before_assert_phase)

    def __write_and_store_script_file_path(self):
        self.__source_setup = SourceSetup(self.__act_phase_handling.source_builder,
                                          self.__execution_directory_structure.test_case_dir,
                                          phases.ACT.section_name)
        self.__act_phase_handling.executor.prepare(self.__source_setup,
                                                   self.configuration.home_dir,
                                                   self.__execution_directory_structure)

    def __act__script_execute(self) -> PartialResult:
        """
        Pre-condition: write has been executed.
        """
        the_phase_step = phase_step.ACT__SCRIPT_EXECUTE
        try:
            self.__write_and_store_script_file_path()
            if self.___step_execution_result.has_custom_stdin:
                file_name = self._custom_stdin_file_name()
                self._run_act_script_with_opened_stdin_file(file_name)
            else:
                self._run_act_script_with_stdin_file(subprocess.DEVNULL)
            return new_partial_result_pass(self.__execution_directory_structure)
        except Exception as ex:
            return PartialResult(PartialResultStatus.IMPLEMENTATION_ERROR,
                                 self.__execution_directory_structure,
                                 PhaseFailureInfo(the_phase_step,
                                                  result.new_failure_details_from_exception(ex)))

    def _run_act_script_with_opened_stdin_file(self, file_name: str):
        try:
            f_stdin = open(file_name)
            self._run_act_script_with_stdin_file(f_stdin)
        finally:
            f_stdin.close()

    def _run_act_script_with_stdin_file(self, f_stdin):
        """
        Pre-condition: write has been executed.
        """
        with open(str(self._eds.result.stdout_file), 'w') as f_stdout:
            with open(str(self._eds.result.stderr_file), 'w') as f_stderr:
                exitcode = self.__act_phase_handling.executor.execute(
                    self.__source_setup,
                    self.configuration.home_dir,
                    self.__execution_directory_structure,
                    StdFiles(f_stdin,
                             StdOutputFiles(f_stdout,
                                            f_stderr)))
                self._store_exit_code(exitcode)

    def __set_pre_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_pre_validate(self.configuration.home_dir))

    def __set_cwd_to_act_dir(self):
        os.chdir(str(self._eds.act_dir))

    def __construct_and_set_eds(self) -> ExecutionDirectoryStructure:
        eds_structure_root = tempfile.mkdtemp(prefix=self.__configuration.execution_directory_root_name_prefix)
        self.__execution_directory_structure = construct_eds(eds_structure_root)

    def __post_eds_environment(self,
                               phase: phases.Phase) -> common.GlobalEnvironmentForPostEdsPhase:
        return common.GlobalEnvironmentForPostEdsPhase(self.__configuration.home_dir,
                                                       self.__execution_directory_structure,
                                                       phase.identifier)

    def __set_post_eds_environment_variables(self):
        os.environ.update(environment_variables.set_at_setup_main(self._eds))

    def __set_assert_environment_variables(self):
        os.environ.update(environment_variables.set_at_assert(self._eds))

    def __run_internal_instructions_phase_step(self,
                                               step: PhaseStep,
                                               instruction_executor: ControlledInstructionExecutor,
                                               phase_contents: SectionContents) -> PartialResult:
        return phase_step_execution.execute_phase(phase_contents,
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  phase_step_execution.ElementHeaderExecutorThatDoesNothing(),
                                                  instruction_executor,
                                                  step,
                                                  self._eds)

    def _custom_stdin_file_name(self) -> str:
        settings = self.___step_execution_result.stdin_settings
        if settings.file_name is not None:
            return settings.file_name
        else:
            file_path = stdin_contents_file(self.__execution_directory_structure)
            write_new_text_file(file_path, settings.contents)
            return str(file_path)


class _ActCommentHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        self.__phase_environment.append.comment_line(line.text)


class _ActInstructionHeaderExecutor(ElementHeaderExecutor):
    def __init__(self,
                 phase_environment: PhaseEnvironmentForScriptGeneration):
        self.__phase_environment = phase_environment

    def apply(self, line: line_source.Line):
        pass
