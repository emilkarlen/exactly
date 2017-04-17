import random
import unittest

from exactly_lib.instructions.utils import instruction_from_parts_for_executing_sub_process as spe_parts
from exactly_lib.instructions.utils import pre_or_post_validation
from exactly_lib.instructions.utils import sub_process_execution as spe
from exactly_lib.instructions.utils.cmd_and_args_resolvers import ConstantCmdAndArgsResolver
from exactly_lib.instructions.utils.instruction_from_parts_for_executing_sub_process import \
    ValidationAndSubProcessExecutionSetup
from exactly_lib.instructions.utils.instruction_parts import InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases.common import PhaseLoggingPaths
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.string import lines_content
from exactly_lib.value_definition.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib_test.act_phase_setups.test_resources import py_program as py
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.utils.sub_process_execution import assert_dir_contains_at_least_result_files
from exactly_lib_test.test_resources.parse import source4
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.python_program_execution import \
    non_shell_args_for_that_executes_source_on_command_line
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as va_str


class Configuration(ConfigurationBase):
    def run_sub_process_test(self,
                             put: unittest.TestCase,
                             source: ParseSource,
                             execution_setup_parser: spe_parts.ValidationAndSubProcessExecutionSetupParser,
                             arrangement,
                             expectation,
                             instruction_name: str = 'instruction-name'):
        self.run_test_with_parser(put,
                                  self._parser(instruction_name,
                                               execution_setup_parser),
                                  source,
                                  arrangement,
                                  expectation)

    def phase(self) -> Phase:
        raise NotImplementedError()

    def instruction_info_for(self, instruction_name: str) -> InstructionInfoForConstructingAnInstructionFromParts:
        raise NotImplementedError()

    def _parser(self, instruction_name: str,
                execution_setup_parser: spe_parts.ValidationAndSubProcessExecutionSetupParser) -> InstructionParser:
        return spe_parts.InstructionParser(self.instruction_info_for(instruction_name),
                                           execution_setup_parser)

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: va.ValueAssertion):
        """
        :param main_side_effects_on_files: An assertion on the SDS
        """
        raise NotImplementedError()

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expect_hard_error_in_main(self) -> Expectation:
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_case_classes = [TestResultIsValidationErrorWhenPreSdsValidationFails,
                         TestResultIsValidationErrorWhenPostSetupValidationFails,
                         TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                         TestInstructionIsErrorWhenExitStatusFromCommandIsNonZero,
                         TestInstructionIsErrorWhenProcessTimesOut,
                         TestEnvironmentVariablesArePassedToSubProcess,
                         TestOutputIsStoredInFilesInInstructionLogDir,
                         TestWhenNonZeroExitCodeTheContentsOfStderrShouldBeIncludedInTheErrorMessage,
                         TestInstructionIsSuccessfulWhenExitStatusFromShellCommandIsZero,
                         ]
    return unittest.TestSuite(
        [tcc(configuration) for tcc in test_case_classes])


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, conf: Configuration):
        super().__init__(conf)
        self.conf = conf


class TestResultIsValidationErrorWhenPreSdsValidationFails(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            ConstantResultValidator(pre_sds='validation error message')
        )
        self.conf.run_sub_process_test(
            self,
            source4(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_failing_validation_pre_sds(va.Equals('validation error message')))


class TestResultIsValidationErrorWhenPostSetupValidationFails(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            ConstantResultValidator(post_setup='validation error message post setup')
        )
        self.conf.run_sub_process_test(
            self,
            source4(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_failing_validation_post_setup(va.Equals('validation error message post setup')))


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        self.conf.run_sub_process_test(
            self,
            source4(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expectation_for_zero_exitcode())


class TestInstructionIsSuccessfulWhenExitStatusFromShellCommandIsZero(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingShellCommandFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        command_that_exits_with_code = shell_commands.command_that_exits_with_code(0)
        self.conf.run_sub_process_test(
            self,
            source4(command_that_exits_with_code),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expectation_for_zero_exitcode())


class TestInstructionIsErrorWhenExitStatusFromCommandIsNonZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_non_zero_status = 'import sys; sys.exit(1)'

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        self.conf.run_sub_process_test(
            self,
            source4(script_that_exists_with_non_zero_status),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expectation_for_non_zero_exitcode())


class TestInstructionIsErrorWhenProcessTimesOut(TestCaseBase):
    def runTest(self):
        timeout_in_seconds = 1
        script_that_sleeps = lines_content(py.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(4))
        program_source_as_single_line = script_that_sleeps.replace('\n', ';')
        source = source4(program_source_as_single_line)

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.arrangement_with_timeout(timeout_in_seconds),
            self.conf.expect_hard_error_in_main())


class TestEnvironmentVariablesArePassedToSubProcess(TestCaseBase):
    def runTest(self):
        var_name = 'TEST_VAR_' + str(random.getrandbits(32))
        var_value = str(random.getrandbits(32))
        expected_sub_process_result = SubProcessResult(exitcode=0,
                                                       stdout=var_value + '\n',
                                                       stderr='')
        environ = {var_name: var_value}
        program = lines_content(py.write_value_of_environment_variable_to_stdout(var_name))
        program_source_as_single_line = program.replace('\n', ';')
        source = source4(program_source_as_single_line)

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        instruction_name = 'name-of-the-instruction'
        source_info = spe.InstructionSourceInfo(source.current_line_number,
                                                instruction_name)
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.arrangement(environ=environ),
            self.conf.expect_success_and_side_effects_on_files(_InstructionLogDirContainsOutFiles(self.conf.phase(),
                                                                                                  source_info,
                                                                                                  expected_sub_process_result)),
            instruction_name=instruction_name)


class TestOutputIsStoredInFilesInInstructionLogDir(TestCaseBase):
    def runTest(self):
        sub_process_result = SubProcessResult(exitcode=0,
                                              stdout='output on stdout',
                                              stderr='output on stderr')
        program = py.program_that_prints_and_exits_with_exit_code(sub_process_result)
        program_source_as_single_line = program.replace('\n', ';')
        source = source4(program_source_as_single_line)
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        instruction_name = 'name-of-the-instruction'
        source_info = spe.InstructionSourceInfo(source.current_line_number,
                                                instruction_name)
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_success_and_side_effects_on_files(_InstructionLogDirContainsOutFiles(self.conf.phase(),
                                                                                                  source_info,
                                                                                                  sub_process_result)),
            instruction_name=instruction_name)


class TestWhenNonZeroExitCodeTheContentsOfStderrShouldBeIncludedInTheErrorMessage(TestCaseBase):
    def runTest(self):
        sub_process_result = SubProcessResult(exitcode=72,
                                              stdout='output on stdout',
                                              stderr='output on stderr')
        program = py.program_that_prints_and_exits_with_exit_code(sub_process_result)
        program_source_as_single_line = program.replace('\n', ';')
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        source = source4(program_source_as_single_line)
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_failure_of_main(va_str.contains('output on stderr')))


class _InstructionLogDirContainsOutFiles(va.ValueAssertion):
    def __init__(self,
                 phase: Phase,
                 source_info: spe.InstructionSourceInfo,
                 expected_files_contents: SubProcessResult):
        self.phase = phase
        self.source_info = source_info
        self.expected_files_contents = expected_files_contents

    def apply(self,
              put: unittest.TestCase,
              sds: SandboxDirectoryStructure,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        logging_paths = PhaseLoggingPaths(sds.log_dir, self.phase.identifier)
        instruction_log_dir = spe.instruction_log_dir(logging_paths, self.source_info)
        assert_dir_contains_at_least_result_files(self.expected_files_contents).apply(put,
                                                                                      instruction_log_dir,
                                                                                      message_builder)


class _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
    spe_parts.ValidationAndSubProcessExecutionSetupParser):
    def __init__(self,
                 validator: pre_or_post_validation.PreOrPostSdsValidator):
        self.validator = validator

    def parse(self, source: ParseSource) -> ValidationAndSubProcessExecutionSetup:
        instruction_argument = source.remaining_part_of_current_line
        source.consume_current_line()
        return ValidationAndSubProcessExecutionSetup(self.validator,
                                                     _resolver_for_execute_py_on_command_line(
                                                         instruction_argument),
                                                     is_shell=False)


class _SetupParserForExecutingShellCommandFromInstructionArgumentOnCommandLine(
    spe_parts.ValidationAndSubProcessExecutionSetupParser):
    def __init__(self,
                 validator: pre_or_post_validation.PreOrPostSdsValidator):
        self.validator = validator

    def parse(self, source: ParseSource) -> ValidationAndSubProcessExecutionSetup:
        instruction_argument = source.remaining_part_of_current_line
        source.consume_current_line()
        return ValidationAndSubProcessExecutionSetup(self.validator,
                                                     ConstantCmdAndArgsResolver(instruction_argument),
                                                     is_shell=True)


def _resolver_for_execute_py_on_command_line(python_source: str) -> spe.CmdAndArgsResolver:
    return ConstantCmdAndArgsResolver(non_shell_args_for_that_executes_source_on_command_line(python_source))


SCRIPT_THAT_EXISTS_WITH_STATUS_0 = 'import sys; sys.exit(0)'


class ConstantResultValidator(pre_or_post_validation.PreOrPostSdsValidator):
    def __init__(self, pre_sds=None,
                 post_setup=None):
        self.pre_sds = pre_sds
        self.post_setup = post_setup

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> str:
        return self.pre_sds

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> str:
        return self.post_setup
