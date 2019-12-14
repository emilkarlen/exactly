import random
import unittest
from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.instructions.multi_phase.utils import \
    instruction_from_parts_for_executing_program as spe_parts
from exactly_lib.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases.common import PhaseLoggingPaths, InstructionSourceInfo
from exactly_lib.test_case.phases.common import instruction_log_dir
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.command_program_sdv import ProgramSdvForCommand
from exactly_lib.util.string import lines_content
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.section_document.test_resources.parse_source import source4
from exactly_lib_test.test_case_utils.test_resources import command_sdvs as test_command_sdvs
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase
from exactly_lib_test.util.process_execution.sub_process_execution import assert_dir_contains_at_least_result_files
from exactly_lib_test.util.test_resources import py_program as py


class Configuration(ConfigurationBase):
    def run_sub_process_test(self,
                             put: unittest.TestCase,
                             source: ParseSource,
                             program_parser: Parser[ProgramSdv],
                             arrangement,
                             expectation,
                             instruction_name: str = 'instruction-name'):
        self.run_test_with_parser(put,
                                  self._parser(instruction_name,
                                               program_parser),
                                  source,
                                  arrangement,
                                  expectation)

    def phase(self) -> Phase:
        raise NotImplementedError()

    def instruction_from_parts_parser(self, parts_parser: InstructionPartsParser) -> InstructionParser:
        raise NotImplementedError()

    def _parser(self,
                instruction_name: str,
                program_parser: Parser[ProgramSdv]) -> InstructionParser:
        parts_parser = spe_parts.parts_parser(instruction_name, program_parser)
        return self.instruction_from_parts_parser(parts_parser)

    def expect_failing_validation_post_setup(self,
                                             assertion_on_error_message: ValueAssertion[str] = asrt.anything_goes()):
        raise NotImplementedError()

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expect_hard_error_in_main(self) -> Expectation:
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_case_classes = [TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
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


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
        self.conf.run_sub_process_test(
            self,
            source4(SCRIPT_THAT_EXISTS_WITH_STATUS_0),
            execution_setup_parser,
            self.conf.arrangement(),
            self.conf.expectation_for_zero_exitcode())


class TestInstructionIsSuccessfulWhenExitStatusFromShellCommandIsZero(TestCaseBase):
    def runTest(self):
        execution_setup_parser = _SetupParserForExecutingShellCommandFromInstructionArgumentOnCommandLine()
        command_that_exits_with_code = shell_commands.command_that_exits_with_code(0)
        self.conf.run_sub_process_test(
            self,
            source4(command_that_exits_with_code),
            execution_setup_parser,
            self.conf.arrangement(),
            self.conf.expectation_for_zero_exitcode())


class TestInstructionIsErrorWhenExitStatusFromCommandIsNonZero(TestCaseBase):
    def runTest(self):
        script_that_exists_with_non_zero_status = 'import sys; sys.exit(1)'

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
        self.conf.run_sub_process_test(
            self,
            source4(script_that_exists_with_non_zero_status),
            execution_setup_parser,
            self.conf.arrangement(),
            self.conf.expectation_for_non_zero_exitcode())


class TestInstructionIsErrorWhenProcessTimesOut(TestCaseBase):
    def runTest(self):
        timeout_in_seconds = 1
        script_that_sleeps = lines_content(py.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(4))
        program_source_as_single_line = script_that_sleeps.replace('\n', ';')
        source = source4(program_source_as_single_line)

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
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

        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
        instruction_name = 'name-of-the-instruction'
        source_info = InstructionSourceInfo(source.current_line_number,
                                            instruction_name)
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.arrangement(environ=environ),
            self.conf.expect_success(_InstructionLogDirContainsOutFiles(self.conf.phase(),
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
        execution_setup_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
        instruction_name = 'name-of-the-instruction'
        source_info = InstructionSourceInfo(source.current_line_number,
                                            instruction_name)
        self.conf.run_sub_process_test(
            self,
            source,
            execution_setup_parser,
            self.conf.arrangement(),
            self.conf.expect_success(_InstructionLogDirContainsOutFiles(self.conf.phase(),
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
        program_parser = _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine()
        source = source4(program_source_as_single_line)
        self.conf.run_sub_process_test(
            self,
            source,
            program_parser,
            self.conf.arrangement(),
            self.conf.expect_failure_of_main(asrt_text_doc.rendered_text_matches(
                asrt_str.contains('output on stderr')
            ))
        )


class _InstructionLogDirContainsOutFiles(ValueAssertionBase[SandboxDirectoryStructure]):
    def __init__(self,
                 phase: Phase,
                 source_info: InstructionSourceInfo,
                 expected_files_contents: SubProcessResult):
        self.phase = phase
        self.source_info = source_info
        self.expected_files_contents = expected_files_contents

    def _apply(self,
               put: unittest.TestCase,
               sds: SandboxDirectoryStructure,
               message_builder: asrt.MessageBuilder):
        logging_paths = PhaseLoggingPaths(sds.log_dir, self.phase.identifier)
        the_instruction_log_dir = instruction_log_dir(logging_paths, self.source_info)
        assert_dir_contains_at_least_result_files(self.expected_files_contents).apply(put,
                                                                                      the_instruction_log_dir,
                                                                                      message_builder)


class _SetupParserForExecutingPythonSourceFromInstructionArgumentOnCommandLine(Parser[ProgramSdv]):
    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        instruction_argument = parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        return ProgramSdvForCommand(
            test_command_sdvs.for_py_source_on_command_line(instruction_argument),
            accumulator.empty())


class _SetupParserForExecutingShellCommandFromInstructionArgumentOnCommandLine(Parser[ProgramSdv]):
    def __init__(self):
        super().__init__()

    def parse_from_token_parser(self, parser: TokenParser) -> ProgramSdv:
        instruction_argument = parser.consume_current_line_as_string_of_remaining_part_of_current_line()
        argument_sdv = string_sdvs.str_constant(instruction_argument)
        return ProgramSdvForCommand(
            command_sdvs.for_shell(argument_sdv),
            accumulator.empty())


SCRIPT_THAT_EXISTS_WITH_STATUS_0 = 'import sys; sys.exit(0)'


class ConstantResultSdvValidator(sdv_validation.SdvValidator):
    def __init__(self,
                 pre_sds: Optional[TextRenderer] = None,
                 post_setup: Optional[TextRenderer] = None):
        self.pre_sds = pre_sds
        self.post_setup = post_setup

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[TextRenderer]:
        return self.pre_sds

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[TextRenderer]:
        return self.post_setup
