import unittest

from exactly_lib.cli.definitions import exit_codes
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing import exit_values
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.cli.program_modes.symbol.test_resources import output
from exactly_lib_test.cli.program_modes.symbol.test_resources import sym_def_instruction as sym_def
from exactly_lib_test.cli.program_modes.symbol.test_resources.source_type_checks import check_case_and_suite
from exactly_lib_test.cli.program_modes.test_resources.test_with_files_in_tmp_dir import Arrangement
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRaisesParseException
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
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
                check_case_and_suite(
                    self,
                    cli_arguments,
                    arrangement=
                    Arrangement(),
                    expectation=
                    asrt_proc_result.is_result_for_empty_stdout(
                        exit_codes.EXIT_INVALID_USAGE
                    )
                )

    def test_invalid_syntax(self):
        file_with_invalid_syntax = File(
            'invalid-syntax.xly',
            lines_content([
                SectionName('nonExistingSection').syntax,
            ]))

        check_case_and_suite(
            self,
            [file_with_invalid_syntax.name],
            Arrangement(
                cwd_contents=DirContents([
                    file_with_invalid_syntax,
                ])
            ),
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.NO_EXECUTION__SYNTAX_ERROR.exit_code
            )
        )

    def test_hard_error_from_instruction_in_conf_phase(self):
        file_with_failing_conf_phase_instruction = File(
            'hard-error.xly',
            lines_content([
                phase_names.CONFIGURATION.syntax,
                sym_def.UNCONDITIONALLY_HARD_ERROR_CONF_PHASE_INSTRUCTION_NAME,
            ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [file_with_failing_conf_phase_instruction.name],
            arrangement=
            Arrangement(
                main_program_config=sym_def.main_program_config(),
                cwd_contents=DirContents([
                    file_with_failing_conf_phase_instruction,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.EXECUTION__HARD_ERROR.exit_code
            )
        )

    def test_invalid_syntax_of_act_phase(self):
        file_with_invalid_syntax = File(
            'invalid-syntax.xly',
            lines_content([
                phase_names.ACT.syntax,
                'invalid contents',
            ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [file_with_invalid_syntax.name],
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

    def test_invalid_symbol_reference(self):
        file_with_invalid_case = File(
            'invalid-symbol-reference.xly',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.reference_to('UNDEFINED_SYMBOL', ValueType.STRING),
            ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [file_with_invalid_case.name],
            arrangement=
            Arrangement(
                main_program_config=sym_def.main_program_config(),
                cwd_contents=DirContents([
                    file_with_invalid_case,
                ])
            ),
            expectation=
            asrt_proc_result.is_result_for_empty_stdout(
                exit_values.EXECUTION__VALIDATION_ERROR.exit_code
            )
        )


class TestSuccessfulScenarios(unittest.TestCase):
    def test_empty_file(self):
        emtpy_test_case_file = File.empty('empty.xly')

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [emtpy_test_case_file.name],
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
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
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
                    output.SymbolSummary(symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )

    def test_single_definition_with_single_reference(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),
                                        sym_def.reference_to(symbol_name, ValueType.STRING),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
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
                    output.SymbolSummary(symbol_name, ValueType.STRING, num_refs=1),
                ])),
            )
        )

    def test_single_reference_to_builtin_symbol(self):
        builtin_symbol = StringSymbolContext.of_constant('BUILTIN_STRING_SYMBOL',
                                                         'builtin string symbol value')
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.reference_to(builtin_symbol.name,
                                                             builtin_symbol.value.value_type),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[
                        sym_def.builtin_symbol(builtin_symbol),
                    ]
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([])),
            )
        )

    def test_single_definition_with_reference_to_builtin_symbol(self):
        builtin_symbol = StringSymbolContext.of_constant('BUILTIN_STRING_SYMBOL',
                                                         'builtin string symbol value')
        user_defined_symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(user_defined_symbol_name,
                                                              symbol_reference_syntax_for_name(builtin_symbol.name)),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
            arrangement=
            Arrangement(
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
                main_program_config=sym_def.main_program_config(
                    builtin_symbols=[
                        sym_def.builtin_symbol(builtin_symbol),
                    ]
                ),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolSummary(user_defined_symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )

    def test_single_definition_with_single_reference_in_act_phase(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File('test.xly',
                                    lines_content([
                                        phase_names.SETUP.syntax,
                                        sym_def.define_string(symbol_name, 'value'),

                                        phase_names.ACT.syntax,
                                        sym_def.reference_to(symbol_name, ValueType.STRING),
                                    ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
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
                    output.SymbolSummary(symbol_name, ValueType.STRING, num_refs=1),
                ])),
            )
        )

    def test_single_definition_with_single_reference_in_act_phase__with_actor_set_in_conf(self):
        symbol_name = 'STRING_SYMBOL'
        case_with_single_def = File(
            'test.xly',
            lines_content([
                phase_names.CONFIGURATION.syntax,

                sym_def.SET_ACTOR_THAT_PARSES_REFERENCES_INSTRUCTION_NAME,

                phase_names.SETUP.syntax,

                sym_def.define_string(symbol_name, 'value'),

                phase_names.ACT.syntax,

                sym_def.reference_to(symbol_name, ValueType.STRING),
            ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
            arrangement=
            Arrangement(
                main_program_config=sym_def.main_program_config(
                    ActorThatRaisesParseException()
                ),
                cwd_contents=DirContents([
                    case_with_single_def,
                ]),
            ),
            expectation=
            asrt_proc_result.sub_process_result(
                exitcode=asrt.equals(exit_codes.EXIT_OK),
                stdout=asrt.equals(output.list_of([
                    output.SymbolSummary(symbol_name, ValueType.STRING, num_refs=1),
                ])),
            )
        )

    def test_definition_and_reference_in_definition(self):
        leaf_name = 'LEAF_SYMBOL_SYMBOL'
        referrer_name = 'REFERRER_SYMBOL'
        case_with_single_def = File(
            'test.xly',
            lines_content([
                phase_names.SETUP.syntax,
                sym_def.define_string(leaf_name, 'value'),
                sym_def.define_string(referrer_name,
                                      symbol_reference_syntax_for_name(leaf_name)),
            ]))

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_single_def.name],
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
                    output.SymbolSummary(leaf_name, ValueType.STRING, num_refs=1),
                    output.SymbolSummary(referrer_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )

    def test_multiple_definition(self):
        setup_symbol_name = 'SETUP_SYMBOL'
        before_assert_symbol_name = 'BEFORE_ASSERT_SYMBOL'
        assert_symbol_name = 'ASSERT_SYMBOL'
        cleanup_symbol_name = 'CLEANUP_SYMBOL'
        case_with_one_def_per_phase = File(
            'test.xly',
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

        check_case_and_suite(
            self,
            symbol_command_arguments=
            [case_with_one_def_per_phase.name],
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
                    output.SymbolSummary(setup_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolSummary(before_assert_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolSummary(assert_symbol_name, ValueType.STRING, num_refs=0),
                    output.SymbolSummary(cleanup_symbol_name, ValueType.STRING, num_refs=0),
                ])),
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
