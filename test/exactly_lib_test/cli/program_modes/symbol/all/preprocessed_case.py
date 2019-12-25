import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.processing import exit_values
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import suite_instructions
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.processing.test_resources import preprocessor_utils
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, File
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidPreprocessor),
        unittest.makeSuite(TestStandaloneCase),
    ])


class TestInvalidPreprocessor(unittest.TestCase):
    def test_preprocessor_that_fails(self):
        valid_file_without_symbol_definitions = empty_file('valid.case')

        py_pgm_that_fails_unconditionally = File(
            'preprocessor.py',
            preprocessor_utils.PREPROCESSOR_THAT_FAILS_UNCONDITIONALLY__PY_SRC
        )

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.py_preprocessing_and_case(py_pgm_that_fails_unconditionally.name,
                                                  valid_file_without_symbol_definitions.name),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    py_pgm_that_fails_unconditionally,
                    valid_file_without_symbol_definitions,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.NO_EXECUTION__PRE_PROCESS_ERROR.exit_code
            )
        )


class TestStandaloneCase(unittest.TestCase):
    def test_single_definition(self):
        symbol_name__before_preproc = 'STRING_SYMBOL__BEFORE_PRE_PROC'
        symbol_name__after_preproc = 'STRING_SYMBOL'

        py_pgm_that_replaces_symbol_name = File(
            'replace.py',
            preprocessor_utils.SEARCH_REPLACE_PREPROCESSOR__PY_SRC
        )

        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name__before_preproc, 'value'),
                                    ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.py_search_replace_preprocessing_and_case(py_pgm_that_replaces_symbol_name.name,
                                                                 symbol_name__before_preproc,
                                                                 symbol_name__after_preproc,
                                                                 case_with_single_def.name),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    py_pgm_that_replaces_symbol_name,
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolSummary(symbol_name__after_preproc, ValueType.STRING, num_refs=0),
                ])),
            )
        )


class TestPreprocessorSpecifiedInSuite(unittest.TestCase):
    def test_definition_in_suite_and_case(self):
        # ARRANGE #

        symbol_in_suite = 'SUITE_STRING_SYMBOL'
        symbol_in_case__before_preproc = 'CASE_STRING_SYMBOL__BEFORE_PRE_PROC'
        symbol_in_case__after_preproc = 'CASE_STRING_SYMBOL'

        suite_with_preprocessor = File(
            'with-preprocessor.suite',
            lines_content([
                section_names.CONFIGURATION.syntax,
                suite_instructions.set_search_replace_preprocessor(
                    symbol_in_case__before_preproc,
                    symbol_in_case__after_preproc
                ),

                phase_names.SETUP.syntax,
                sym_def.define_string(symbol_in_suite, 'suite-value'),
            ])
        )

        case_with_single_def = File(
            'test.case',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.define_string(symbol_in_case__before_preproc, 'case-value'),
            ]))

        # ACT & ASSERT #

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.explicit_suite_and_case(suite_with_preprocessor.name,
                                                case_with_single_def.name),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    suite_with_preprocessor,
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolSummary(symbol_in_suite, ValueType.STRING, num_refs=0),
                    output.SymbolSummary(symbol_in_case__after_preproc, ValueType.STRING, num_refs=0),
                ])),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
