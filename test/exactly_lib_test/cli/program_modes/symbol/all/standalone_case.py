import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing import exit_values
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import cl_arguments as symbol_args
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.test_resources import test_with_files_in_tmp_dir
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRaisesParseException
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, File, empty_dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestFailingScenarios(unittest.TestCase):

    def test_invalid_arguments(self):
        # ARRANGE #
        file_name = 'file.xly'

        cases = [
            NameAndValue('file-arg is missing',
                         []),

            NameAndValue('file-arg is not existing',
                         [file_name]),

        ]
        for case in cases:
            with self.subTest(case.name):
                cli_arguments = case.value
                # ACT & ASSERT #
                test_with_files_in_tmp_dir.check(
                    self,
                    symbol_args.arguments(cli_arguments),
                    arrangement=
                    Arrangement(),
                    expectation=
                    asrt_proc_result.is_result_for_empty_stdout(
                        exit_codes.EXIT_INVALID_USAGE
                    )
                )

    def test_invalid_type_of_file_arguments(self):
        # ARRANGE #
        a_dir = empty_dir('dir.xly')
        test_with_files_in_tmp_dir.check(
            self,
            symbol_args.arguments([a_dir.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([a_dir])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.NO_EXECUTION__SYNTAX_ERROR.exit_code
            )
        )

    def test_invalid_syntax(self):
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

    def test_invalid_syntax_of_act_phase(self):
        file_with_invalid_syntax = File(
            'invalid-syntax.case',
            lines_content([
                phase_names.ACT.syntax,
                'invalid contents',
            ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([file_with_invalid_syntax.name]),
            arrangement=
            Arrangement(
                main_program_config=sym_def.main_program_config(
                    ActorThatRaisesParseException()
                ),
                cwd_contents=DirContents([
                    file_with_invalid_syntax,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.EXECUTION__VALIDATION_ERROR.exit_code
            )
        )


class TestSuccessfulScenarios(unittest.TestCase):
    def test_empty_file(self):
        emtpy_test_case_file = empty_file('empty.case')

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([emtpy_test_case_file.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    emtpy_test_case_file,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_codes.EXIT_OK
            )
        )

    def test_single_definition(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),
                                    ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([case_with_single_def.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolReport(symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )

    def test_single_definition_with_single_reference(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),
                                        sym_def.reference_to(symbol_name, ValueType.STRING),
                                    ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([case_with_single_def.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolReport(symbol_name, ValueType.STRING, num_refs=1),
                ])),
            )
        )

    def test_single_definition_with_single_reference_in_act_phase(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.case',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),

                                        phase_names.ACT.syntax,
                                        sym_def.reference_to(symbol_name, ValueType.STRING),
                                    ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([case_with_single_def.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolReport(symbol_name, ValueType.STRING, num_refs=1),
                ])),
            )
        )

    def test_definition_and_reference_in_definition(self):
        leaf_name = 'LEAF_SYMBOL_SYMBOL'
        referrer_name = 'REFERRER_SYMBOL'
        case_with_single_def = File(
            'test.case',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.define_string(leaf_name, 'value'),
                sym_def.define_string(referrer_name,
                                      symbol_reference_syntax_for_name(leaf_name)),
            ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([case_with_single_def.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolReport(leaf_name, ValueType.STRING, num_refs=1),
                    output.SymbolReport(referrer_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )

    def test_multiple_definition(self):
        setup_symbol_name = 'SETUP_SYMBOL'
        before_assert_symbol_name = 'BEFORE_ASSERT_SYMBOL'
        assert_symbol_name = 'ASSERT_SYMBOL'
        cleanup_symbol_name = 'CLEANUP_SYMBOL'
        case_with_one_def_per_phase = File(
            'test.case',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.define_string(setup_symbol_name, setup_symbol_name + 'value'),

                phase_names.BEFORE_ASSERT.syntax,
                sym_def.define_string(before_assert_symbol_name,
                                      before_assert_symbol_name + 'value'),

                phase_names.ASSERT.syntax,
                sym_def.define_string(assert_symbol_name, assert_symbol_name + 'value'),

                phase_names.CLEANUP.syntax,
                sym_def.define_string(cleanup_symbol_name,
                                      cleanup_symbol_name + 'value'),
            ]))

        test_with_files_in_tmp_dir.check(
            self,
            command_line_arguments=
            symbol_args.arguments([case_with_one_def_per_phase.name]),
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_one_def_per_phase,
                ]),
                main_program_config=sym_def.main_program_config(),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolReport(setup_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolReport(before_assert_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolReport(assert_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolReport(cleanup_symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
