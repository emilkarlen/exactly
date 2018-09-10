import unittest

from exactly_lib.execution.configuration import PredefinedProperties
from exactly_lib.processing import processors
from exactly_lib.test_suite import processing as sut
from exactly_lib.test_suite.processing import TestCaseProcessorConstructor
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.str_std_out_files import StringStdOutFiles
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_suite.processing.test_resources import symbol_defs_should_not_leak as tr
from exactly_lib_test.test_suite.processing.test_resources.processor import new_processor
from exactly_lib_test.test_suite.test_resources.suite_reporting import ExecutionTracingRootSuiteReporter


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


INSTR_DEFINE = 'define'
INSTR_REGISTER_EXISTENCE = 'register_existence_of'

SYMBOL_NAME = 'DEFINED_IN_FIRST_CASE'

FORMAT_MAP = {
    'define': INSTR_DEFINE,
    'register_existence_of': INSTR_REGISTER_EXISTENCE,
    'symbol_name': SYMBOL_NAME,
}

CASE_THAT_DEFINES_SYMBOL = """\
[setup]

{define} {symbol_name}
"""

CASE_THAT_REGISTERS_EXISTENCE_OF_SYMBOL = """\
[setup]

{register_existence_of} {symbol_name}
"""

CASE_1_FILE = File('1.case',
                   CASE_THAT_DEFINES_SYMBOL.format_map(FORMAT_MAP))

CASE_2_FILE = File('2.case',
                   CASE_THAT_REGISTERS_EXISTENCE_OF_SYMBOL.format_map(FORMAT_MAP))

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
                    processor = new_processor_with_no_symbols(registry,
                                                              case_processor_case.value)
                    # ACT #

                    return_value = processor.process(suite_file_path, StringStdOutFiles().stdout_files)

                    # ASSERT #

                    self.assertEqual(ExecutionTracingRootSuiteReporter.VALID_SUITE_EXIT_CODE,
                                     return_value,
                                     'Sanity check of result indicator')
                    self.assertFalse(registry.observation)


def new_processor_with_no_symbols(registry: tr.Registry,
                                  test_case_processor_constructor: TestCaseProcessorConstructor) -> sut.Processor:
    return new_processor(
        {
            INSTR_DEFINE: tr.InstructionParserForDefine(),
            INSTR_REGISTER_EXISTENCE: tr.InstructionParserForRegistersExistenceOfSymbol(registry),
        }
        ,
        test_case_processor_constructor,
        PredefinedProperties({}, empty_symbol_table())
    )
