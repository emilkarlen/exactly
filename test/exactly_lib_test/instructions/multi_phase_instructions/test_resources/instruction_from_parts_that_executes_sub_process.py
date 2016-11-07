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
from exactly_lib.test_case.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.configuration import ConfigurationBase
from exactly_lib_test.test_resources.parse import new_source2
from exactly_lib_test.test_resources.python_program_execution import \
    non_shell_args_for_that_executes_source_on_command_line
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class Configuration(ConfigurationBase):
    def run_sub_process_test(self,
                             put: unittest.TestCase,
                             source: SingleInstructionParserSource,
                             execution_setup_parser: spe_parts.ValidationAndSubProcessExecutionSetupParser,
                             arrangement,
                             expectation):
        instruction_check.check(put,
                                self._parser('instruction-name',
                                             execution_setup_parser),
                                source,
                                arrangement,
                                expectation)

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

    def expectation_for_non_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self) -> Expectation:
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    test_case_classes = [TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                         TestInstructionIsErrorWhenExitStatusFromCommandIsNonZero,
                         TestResultIsValidationErrorWhenPreSdsValidationFails]
    return unittest.TestSuite(
        [tcc(configuration) for tcc in test_case_classes])


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, conf: Configuration):
        super().__init__(conf)
        self.conf = conf


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
            self.conf.expect_failing_validation_pre_eds())


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
