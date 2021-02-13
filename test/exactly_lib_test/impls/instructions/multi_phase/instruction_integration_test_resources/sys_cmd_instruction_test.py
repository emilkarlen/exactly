import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.impls.actors.program.test_resources import tmp_dir_in_path_with_files
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.impls.instructions.multi_phase.test_resources import sys_cmd
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.impls.types.program.test_resources import program_arguments
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import path_arguments
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.programs import py_programs


class Configuration(ConfigurationBase):
    def expectation_for_non_zero_exitcode(self):
        raise NotImplementedError()

    def expectation_for_zero_exitcode(self):
        raise NotImplementedError()


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite([
        suite_for_documentation_instance(configuration.documentation()),
        suite_for_cases(configuration,
                        [
                            TestParseFailsWhenThereAreNoArguments,
                            TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero,
                            TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero,
                            TestValidationOfArguments,
                        ])
    ])


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf


class TestParseFailsWhenThereAreNoArguments(TestCaseBase):
    def runTest(self):
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                self.conf.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestValidationOfArguments(TestCaseBase):
    def runTest(self):
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with(0)
        )
        cases = [
            NameAndValue(
                'pre sds',
                (
                    RelOptionType.REL_HDS_CASE,
                    self.conf.expect_failing_validation_pre_sds(),
                ),
            ),
            NameAndValue(
                'post sds',
                (
                    RelOptionType.REL_ACT,
                    self.conf.expect_hard_error_of_main__any(),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                arguments = sys_cmd.command_line(
                    exe_file.name,
                    program_arguments.existing_file(
                        path_arguments.RelOptPathArgument('non-existing', case.value[0])
                    ),
                )
                with tmp_dir_in_path_with_files(fs.DirContents([exe_file])) as env:
                    self.conf.run_single_line_test_with_source_variants_and_source_check(
                        self,
                        arguments.as_str,
                        self.conf.arrangement(environ=env),
                        case.value[1],
                    )


class TestInstructionIsSuccessfulWhenExitStatusFromCommandIsZero(TestCaseBase):
    def runTest(self):
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with(0)
        )
        with tmp_dir_in_path_with_files(fs.DirContents([exe_file])) as env:
            instruction_argument = exe_file.name
            self.conf.run_single_line_test_with_source_variants_and_source_check(
                self,
                instruction_argument,
                self.conf.arrangement(environ=env),
                self.conf.expectation_for_zero_exitcode(),
            )


class TestInstructionIsHardErrorWhenExitStatusFromCommandIsNonZero(TestCaseBase):
    def runTest(self):
        non_zero_exit_code = 1
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with(non_zero_exit_code)
        )
        with tmp_dir_in_path_with_files(fs.DirContents([exe_file])) as env:
            instruction_argument = exe_file.name
            self.conf.run_single_line_test_with_source_variants_and_source_check(
                self,
                instruction_argument,
                self.conf.arrangement(environ=env),
                self.conf.expectation_for_non_zero_exitcode(),
            )
