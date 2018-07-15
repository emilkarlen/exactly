import pathlib
import unittest

from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.processing import processors
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.act_phase_source_parser import ActPhaseParser
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.test_case import os_services
from exactly_lib.test_suite import enumeration
from exactly_lib.test_suite import execution as sut
from exactly_lib.test_suite import suite_hierarchy_reading
from exactly_lib.test_suite.execution import TestCaseProcessorConstructor
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.section_document.test_resources.element_parsers import SectionElementParserThatRaisesSourceError
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_suite.execution.test_resources import env_vars_should_not_leak as tr
from exactly_lib_test.test_suite.execution.test_resources.list_recording_instructions import instruction_name_extractor
from exactly_lib_test.test_suite.test_resources.execution_utils import \
    test_case_handling_setup_with_identity_preprocessor
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingReporterFactory, \
    ExecutionTracingRootSuiteReporter


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


INSTR_SET = 'set'
INSTR_REGISTER_EXISTENCE = 'register_value_of'
INSTR_ABORT_TEST_IF_VAR_EXISTS = 'abort_test_if_exists'

VAR_NAME = 'SET_IN_FIRST_CASE_34654765423450'
VAR_VALUE = 'value-from-first-case'

FORMAT_MAP = {
    'set': INSTR_SET,
    'abort_test_if_exists': INSTR_ABORT_TEST_IF_VAR_EXISTS,
    'register_existence_of': INSTR_REGISTER_EXISTENCE,
    'var_name': VAR_NAME,
    'var_value': VAR_VALUE,
}

CASE_THAT_MODIFIES_ENV_VARS = """\
[setup]

{abort_test_if_exists} {var_name}

{set} {var_name} = {var_value}
"""

CASE_THAT_REGISTERS_VAR_VALUE = """\
[setup]

{register_existence_of} {var_name}
"""

CASE_1_FILE = File('1.case',
                   CASE_THAT_MODIFIES_ENV_VARS.format_map(FORMAT_MAP))

CASE_2_FILE = File('2.case',
                   CASE_THAT_REGISTERS_VAR_VALUE.format_map(FORMAT_MAP))

SUITE_WITH_CASES = """\
[cases]

{case_1_file}
{case_2_file}
""".format(
    case_1_file=CASE_1_FILE.file_name,
    case_2_file=CASE_2_FILE.file_name,
)


class Test(unittest.TestCase):
    def test_that_value_set_in_first_case_does_not_leak_to_second_case(self):
        # ARRANGE #

        containing_suite_file = File('test.suite', SUITE_WITH_CASES)
        suite_and_case_files = DirContents([
            containing_suite_file,
            CASE_1_FILE,
            CASE_2_FILE,
        ])

        case_processors = [
            NameAndValue('processor_that_should_not_pollute_current_process',
                         processors.new_processor_that_should_not_pollute_current_process),
            NameAndValue('processor_that_is_allowed_to_pollute_current_process',
                         processors.new_processor_that_is_allowed_to_pollute_current_process),
        ]
        with tmp_dir(suite_and_case_files) as tmp_dir_path:
            suite_file_path = tmp_dir_path / containing_suite_file.file_name

            for case_processor_case in case_processors:
                with self.subTest(case_processor_case.name):
                    registry = tr.Registry()
                    executor = new_executor(registry,
                                            case_processor_case.value,
                                            suite_file_path)
                    # ACT #

                    return_value = executor.execute()

                    # ASSERT #

                    self.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')
                    self.assertFalse(registry.observation)


def new_executor(registry: tr.Registry,
                 test_case_processor_constructor: TestCaseProcessorConstructor,
                 suite_root_file_path: pathlib.Path) -> sut.Executor:
    test_case_definition = TestCaseDefinition(
        TestCaseParsingSetup(instruction_name_extractor,
                             _instruction_set(registry),
                             ActPhaseParser()),
        PredefinedProperties(empty_symbol_table()))
    default_configuration = processors.Configuration(test_case_definition,
                                                     test_case_handling_setup_with_identity_preprocessor(),
                                                     os_services.DEFAULT_ACT_PHASE_OS_PROCESS_EXECUTOR,
                                                     False,
                                                     sandbox_dir_resolving.mk_tmp_dir_with_prefix('test-suite-'))

    return sut.Executor(default_configuration,
                        StringStdOutFiles().stdout_files,
                        suite_hierarchy_reading.Reader(
                            suite_hierarchy_reading.Environment(
                                SectionElementParserThatRaisesSourceError(),
                                test_case_definition.parsing_setup,
                                default_configuration.default_handling_setup)
                        ),
                        ExecutionTracingReporterFactory(),
                        enumeration.DepthFirstEnumerator(),
                        test_case_processor_constructor,
                        suite_root_file_path,
                        )


def _instruction_set(registry: tr.Registry) -> InstructionsSetup:
    return tr.instruction_setup({
        INSTR_SET: tr.InstructionParserForSet(),
        INSTR_REGISTER_EXISTENCE: tr.InstructionParserForRegistersExistenceOfEnvVar(registry),
        INSTR_ABORT_TEST_IF_VAR_EXISTS: tr.InstructionParserForAbortsIfEnvVarExists(),
    })
