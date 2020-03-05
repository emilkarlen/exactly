import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.logic.program.program_sdv import ProgramStv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.logic.test_resources.logic_symbol_utils import container_of_program_sdv
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__ref
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import ExecutionExpectation, Expectation, \
    ParseExpectation, arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import integration_check
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.program.test_resources.assertions import assert_process_result_data
from exactly_lib_test.test_case_utils.string_transformers.test_resources import test_transformers_setup
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_with_stdout_stderr_exit_code
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReferenceProgram),
        unittest.makeSuite(TestValidationOfProgramShouldIncludeValidationOfTransformer),

    ])


class TestSymbolReferenceProgram(unittest.TestCase):
    def test_without_transformation(self):
        # ARRANGE #

        stdout_contents = 'output on stdout'
        stderr_contents = 'output on stderr'

        exit_code_cases = [0, 72]

        transformation_cases = [
            NIE(
                'stdout',
                stdout_contents,
                ProcOutputFile.STDOUT,
            ),
            NIE(
                'stderr',
                stderr_contents,
                ProcOutputFile.STDERR,
            ),
        ]
        for exit_code_case in exit_code_cases:
            for transformation_case in transformation_cases:
                with self.subTest(exit_code=exit_code_case,
                                  transformation=transformation_case.name):
                    python_source = py_pgm_with_stdout_stderr_exit_code(stdout_contents,
                                                                        stderr_contents,
                                                                        exit_code_case)

                    sdv_of_referred_program = program_sdvs.for_py_source_on_command_line(python_source)

                    program_that_executes_py_source = NameAndValue(
                        'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                        sdv_of_referred_program
                    )

                    source = parse_source_of(
                        pgm_args.symbol_ref_command_line(sym_ref_args.sym_ref_cmd_line(
                            program_that_executes_py_source.name)))

                    symbols = SymbolTable({
                        program_that_executes_py_source.name:
                            container_of_program_sdv(program_that_executes_py_source.value)
                    })

                    # ACT & ASSERT #

                    integration_check.CHECKER.check(
                        self,
                        source,
                        transformation_case.input_value,
                        logic_integration_check.arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        logic_integration_check.Expectation(
                            logic_integration_check.ParseExpectation(
                                symbol_references=asrt.matches_sequence([
                                    asrt_pgm.is_program_reference_to(program_that_executes_py_source.name),
                                ]),
                            ),
                            logic_integration_check.ExecutionExpectation(
                                main_result=assert_process_result_data(
                                    exitcode=asrt.equals(exit_code_case),
                                    stdout_contents=asrt.equals(stdout_contents),
                                    stderr_contents=asrt.equals(stderr_contents),
                                    contents_after_transformation=asrt.equals(transformation_case.expected_value),
                                )
                            )
                        )
                    )

    def test_with_transformation(self):
        # ARRANGE #

        stdout_contents = 'output on stdout'
        stderr_contents = 'output on stderr'

        exit_code_cases = [0, 72]

        to_upper_transformer = test_transformers_setup.TO_UPPER_CASE_TRANSFORMER

        transformation_cases = [
            NIE(
                'stdout',
                stdout_contents.upper(),
                ProcOutputFile.STDOUT,
            ),
            NIE(
                'stderr',
                stderr_contents.upper(),
                ProcOutputFile.STDERR,
            ),
        ]
        for exit_code_case in exit_code_cases:
            for transformation_case in transformation_cases:
                with self.subTest(exit_code=exit_code_case,
                                  transformation=transformation_case.name):
                    python_source = py_pgm_with_stdout_stderr_exit_code(stdout_contents,
                                                                        stderr_contents,
                                                                        exit_code_case)

                    program_that_executes_py_source = NameAndValue(
                        'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                        program_sdvs.for_py_source_on_command_line(python_source)
                    )

                    source = pgm_args.symbol_ref_command_elements(
                        program_that_executes_py_source.name,
                        transformation=to_upper_transformer.name
                    ).as_remaining_source

                    symbols = SymbolTable({
                        program_that_executes_py_source.name:
                            container_of_program_sdv(program_that_executes_py_source.value),

                        to_upper_transformer.name:
                            test_transformers_setup.symbol_container_of(
                                to_upper_transformer.value
                            )
                    })

                    # ACT & ASSERT #

                    integration_check.CHECKER.check(
                        self,
                        source,
                        transformation_case.input_value,
                        logic_integration_check.arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        logic_integration_check.Expectation(
                            logic_integration_check.ParseExpectation(
                                symbol_references=asrt.matches_sequence([
                                    asrt_pgm.is_program_reference_to(program_that_executes_py_source.name),
                                    is_reference_to_string_transformer__ref(to_upper_transformer.name),
                                ]),
                            ),
                            logic_integration_check.ExecutionExpectation(
                                main_result=assert_process_result_data(
                                    exitcode=asrt.equals(exit_code_case),
                                    stdout_contents=asrt.equals(stdout_contents),
                                    stderr_contents=asrt.equals(stderr_contents),
                                    contents_after_transformation=asrt.equals(transformation_case.expected_value),
                                )
                            )
                        )
                    )


class TestValidationOfProgramShouldIncludeValidationOfTransformer(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_symbol = NameAndValue(
            'A_PROGRAM',
            ProgramStv(program_sdvs.arbitrary_sdv__without_symbol_references())
        )

        pgm_and_args_cases = [
            NameAndValue('shell command',
                         pgm_args.shell_command('shell-command arg')
                         ),
            NameAndValue('system command',
                         pgm_args.system_program_argument_elements('system command arg')
                         ),
            NameAndValue('python',
                         pgm_args.interpret_py_source_elements('exit(0)')
                         ),
            NameAndValue('symbol reference',
                         pgm_args.symbol_ref_command_elements(program_symbol.name, [])
                         ),
        ]
        for pgm_and_args_case in pgm_and_args_cases:
            for validation_case in failing_validation_cases():
                arguments = pgm_and_args_case.value.followed_by_lines(
                    [validation_case.value.transformer_arguments_elements]
                )

                symbols = symbol_table_from_name_and_sdvs([
                    program_symbol,
                    validation_case.value.symbol_context.name_and_sdtv,
                ])

                with self.subTest(pgm_and_args_case=pgm_and_args_case.name,
                                  validation_case=validation_case.name):
                    # ACT & ASSERT #
                    integration_check.CHECKER.check(
                        self,
                        arguments.as_remaining_source,
                        ProcOutputFile.STDOUT,
                        arrangement_w_tcds(
                            symbols=symbols
                        ),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.anything_goes(),
                            ),
                            ExecutionExpectation(
                                validation=validation_case.value.expectation,
                            )
                        )
                    )


def parse_source_of(single_line: ArgumentElementsRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
