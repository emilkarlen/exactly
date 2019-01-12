import unittest

from exactly_lib.definitions.formatting import SectionName
from exactly_lib.processing import exit_values
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestInvalidCaseFileSyntax)


class TestInvalidCaseFileSyntax(unittest.TestCase):
    def test_missing_test_case_file_argument(self):
        file_with_invalid_syntax = File(
            'invalid-syntax.case',
            lines_content([
                SectionName('nonExistingSection').syntax,
            ]))

        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments([file_with_invalid_syntax.name]),
            Arrangement(
                cwd_contents=DirContents([
                    file_with_invalid_syntax,
                ])
            ),
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.NO_EXECUTION__SYNTAX_ERROR.exit_code
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
