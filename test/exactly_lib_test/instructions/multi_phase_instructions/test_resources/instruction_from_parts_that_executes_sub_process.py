import pathlib
import unittest

from exactly_lib.instructions.utils import instruction_from_parts_for_executing_sub_process as spe_parts
from exactly_lib.instructions.utils import pre_or_post_validation
from exactly_lib.instructions.utils import sub_process_execution as spe
from exactly_lib.instructions.utils.cmd_and_args_resolvers import ConstantCmdAndArgsResolver
from exactly_lib.instructions.utils.instruction_from_parts_for_executing_sub_process import \
    ValidationAndSubProcessExecutionSetup
from exactly_lib.instructions.utils.instruction_parts import InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource, SingleInstructionParser
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases.common import PhaseLoggingPaths
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.act_phase_setups.test_resources.py_program import program_that_prints_and_exits_with_exit_code
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.instructions.utils.sub_process_execution import assert_dir_contains_at_least_result_files
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.programs.python_program_execution import \
    non_shell_args_for_that_executes_source_on_command_line
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as va
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as va_str


class Configuration(ConfigurationBase):
    def run_sub_process_test(self,
                             put: unittest.TestCase,
                             source: SingleInstructionParserSource,
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
                execution_setup_parser: spe_parts.ValidationAndSubProcessExecutionSetupParser) -> SingleInstructionParser:
        return spe_parts.InstructionParser(self.instruction_info_for(instruction_name),
                                           execution_setup_parser)

    def expect_success_and_side_effects_on_files(self,
                                                 main_side_effects_on_files: va.ValueAssertion):
        """
        :param main_side_effects_on_files: An assertion on the EDS
        """
        raise NotImplementedError()

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: va.ValueAssertion = va.anything_goes()):
        raise NotImplementedError()

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_case_classes = [TestResultIsValidationErrorWhenPreSdsValidationFails,
                         TestResultIsValidationErrorWhenPostSetupValidationFails,
                         TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                         TestInstructionIsErrorWhenExitStatusFromCommandIsNonZero,
                         TestOutputIsStoredInFilesInInstructionLogDir,
                         TestWhenNonZeroExitCodeTheContentsOfStderrShouldBeIncludedInTheErrorMessage,
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
            new_source2(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_failing_validation_pre_eds(va.Equals('validation error message')))


class TestResultIsValidationErrorWhenPostSetupValidationFails(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            ConstantResultValidator(post_setup='validation error message post setup')
        )
        self.conf.run_sub_process_test(
            self,
            new_source2(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expect_failing_validation_post_setup(va.Equals('validation error message post setup')))


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        self.conf.run_sub_process_test(
            self,
            new_source2(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
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
            new_source2(script_that_exists_with_non_zero_status),
            execution_setup_parser,
            self.conf.empty_arrangement(),
            self.conf.expectation_for_non_zero_exitcode())


class TestOutputIsStoredInFilesInInstructionLogDir(TestCaseBase):
    def runTest(self):
        sub_process_result = SubProcessResult(exitcode=0,
                                              stdout='output on stdout',
                                              stderr='output on stderr')
        program = program_that_prints_and_exits_with_exit_code(sub_process_result)
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        source = new_source2(program)
        instruction_name = 'name-of-the-instruction'
        source_info = spe.InstructionSourceInfo(source.line_sequence.first_line.line_number,
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
        program = program_that_prints_and_exits_with_exit_code(sub_process_result)
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(
            pre_or_post_validation.ConstantSuccessValidator())
        source = new_source2(program)
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
                 validator: pre_or_post_validation.PreOrPostEdsValidator):
        self.validator = validator

    def apply(self, source: SingleInstructionParserSource) -> ValidationAndSubProcessExecutionSetup:
        return ValidationAndSubProcessExecutionSetup(self.validator,
                                                     _resolver_for_execute_py_on_command_line(
                                                         source.instruction_argument),
                                                     is_shell=False)


def _resolver_for_execute_py_on_command_line(python_source: str) -> spe.CmdAndArgsResolver:
    return ConstantCmdAndArgsResolver(non_shell_args_for_that_executes_source_on_command_line(python_source))


SCRIPT_THAT_EXISTS_WITH_STATUS_0 = 'import sys; sys.exit(0)'


class ConstantResultValidator(pre_or_post_validation.PreOrPostEdsValidator):
    def __init__(self, pre_sds=None,
                 post_setup=None):
        self.pre_sds = pre_sds
        self.post_setup = post_setup

    def validate_pre_eds_if_applicable(self, home_dir_path: pathlib.Path) -> str:
        return self.pre_sds

    def validate_post_eds_if_applicable(self, sds: SandboxDirectoryStructure) -> str:
        return self.post_setup
