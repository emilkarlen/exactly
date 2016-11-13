from exactly_lib.instructions.utils import sub_process_execution as spe
from exactly_lib.instructions.utils.instruction_parts import MainStepExecutor, InstructionParts, \
    InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths, \
    TestCaseInstructionExecutedInSandbox
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh


class SubProcessExecutionSetup:
    def __init__(self,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        self.cmd_and_args_resolver = cmd_and_args_resolver
        self.is_shell = is_shell


class ValidationAndSubProcessExecutionSetup(SubProcessExecutionSetup):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        super().__init__(cmd_and_args_resolver, is_shell)
        self.validator = validator


class MainStepExecutorForSubProcess(MainStepExecutor):
    """
    A MainStepExecutor for executing an external program as a sub process.
    """

    def __init__(self,
                 source_info: spe.InstructionSourceInfo,
                 setup: SubProcessExecutionSetup):
        self._source_info = source_info
        self._setup = setup

    def apply(self,
              environment: InstructionEnvironmentForPostSdsStep,
              logging_paths: PhaseLoggingPaths,
              os_services: OsServices) -> spe.ResultAndStderr:
        # The structures and implementation here does not feel good, - a candidate for refactoring!
        # E.g. ExecuteInfo may be unnecessary.
        # This implementation was copied from earlier code that was existed in many places - so that
        # it had the purpose of being reusable in many places!
        # After the refactoring that introduced this class, this implementation should perhaps be refactored.
        # But no time for this now!
        execute_info = spe.ExecuteInfo(self._source_info,
                                       self._setup.cmd_and_args_resolver.resolve(environment.home_and_sds))
        executor = spe.ExecutorThatStoresResultInFilesInDir(
            self._setup.is_shell,
            spe.settings_from_instruction_env(environment))
        return spe.execute_and_read_stderr_if_non_zero_exitcode(execute_info, executor, logging_paths)

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices) -> sh.SuccessOrHardError:
        return spe.result_to_sh(self.apply(environment, logging_paths, os_services))

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           logging_paths: PhaseLoggingPaths,
                           os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return spe.result_to_pfh(self.apply(environment, logging_paths, os_services))


class ValidationAndSubProcessExecutionSetupParser:
    def apply(self, source: SingleInstructionParserSource) -> ValidationAndSubProcessExecutionSetup:
        raise NotImplementedError()


class InstructionParser(SingleInstructionParser):
    def __init__(self,
                 instruction_info: InstructionInfoForConstructingAnInstructionFromParts,
                 setup_parser: ValidationAndSubProcessExecutionSetupParser):
        self.instruction_info = instruction_info
        self.setup_parser = setup_parser

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstructionExecutedInSandbox:
        source_info = spe.InstructionSourceInfo(source.line_sequence.first_line.line_number,
                                                self.instruction_info.instruction_name)
        setup = self.setup_parser.apply(source)
        return self.instruction_info.instruction_parts_2_instruction_function(
            InstructionParts(setup.validator,
                             MainStepExecutorForSubProcess(source_info, setup)))
