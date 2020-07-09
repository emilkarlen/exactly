import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite.file_names import DEFAULT_SUITE_FILE
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.files.file_structure import empty_dir
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestFailingScenarios(unittest.TestCase):

    def test_file_is_dir_that_do_not_contain_default_suite_file(self):
        # ARRANGE #
        a_dir = empty_dir('dir')
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments__suite([a_dir.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([a_dir])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_INVALID_USAGE
            )
        )


class TestSuccessfulScenarios(unittest.TestCase):
    def test_single_definition_in_default_suite_file(self):
        symbol_name = 'STRING_SYMBOL'
        suite_with_single_def = File(DEFAULT_SUITE_FILE,
                                     lines_content([
                                         phase_names.SETUP.syntax,
                                         sym_def.define_string(symbol_name, 'value'),
                                     ]))
        dir_arg = Dir('a-dir', [suite_with_single_def])

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments__suite([dir_arg.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    dir_arg,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolSummary(symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
