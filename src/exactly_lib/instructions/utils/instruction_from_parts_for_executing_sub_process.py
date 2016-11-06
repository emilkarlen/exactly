from exactly_lib.instructions.utils import sub_process_execution as spe
from exactly_lib.instructions.utils.instruction_parts import MainStepExecutor
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


class SubProcessExecutionSetup:
    def __init__(self,
                 source_info: spe.InstructionSourceInfo,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        self.cmd_and_args_resolver = cmd_and_args_resolver
        self.source_info = source_info
        self.is_shell = is_shell


class ValidationAndSubProcessExecutionSetup(SubProcessExecutionSetup):
    def __init__(self,
                 source_info: spe.InstructionSourceInfo,
                 validator: PreOrPostEdsValidator,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        super().__init__(source_info, cmd_and_args_resolver, is_shell)
        self.validator = validator


class MainStepExecutorForSubProcess(MainStepExecutor):
    """
    A MainStepExecutor for executing an external program as a sub process.
    """

    def __init__(self, setup: SubProcessExecutionSetup):
        self._setup = setup

    def apply(self,
              environment: InstructionEnvironmentForPostSdsStep,
              logging_paths: PhaseLoggingPaths,
              os_services: OsServices) -> spe.ResultAndStderr:
        execute_info = spe.ExecuteInfo(self._setup.source_info,
                                       self._setup.cmd_and_args_resolver.resolve(environment.home_and_sds))
        executor = spe.ExecutorThatStoresResultInFilesInDir(self._setup.is_shell)
        return spe.execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, logging_paths)

    def apply_sh(self,
                 environment: InstructionEnvironmentForPostSdsStep,
                 logging_paths: PhaseLoggingPaths,
                 os_services: OsServices) -> sh.SuccessOrHardError:
        return spe.result_to_sh(self.apply(environment, logging_paths, os_services))

    def apply_pfh(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  logging_paths: PhaseLoggingPaths,
                  os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return spe.result_to_pfh(self.apply(environment, logging_paths, os_services))
