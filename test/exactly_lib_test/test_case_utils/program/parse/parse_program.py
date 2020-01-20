import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.parse import parse_system_program
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_execution_check as pgm_exe_check
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSymbolReferenceProgram),
        unittest.makeSuite(TestParseSystemProgram),
        unittest.makeSuite(TestValidationOfProgramShouldIncludeValidationOfTransformer),

    ])


class TestParseSystemProgram(unittest.TestCase):
    def test(self):
        # ARRANGE #
        program_name_case = parse_system_program.ProgramNameCase(
            'constant name',
            source_element='program_name',
            expected_resolved_value='program_name',
            expected_symbol_references=[],
        )
        arguments_case = parse_system_program.ArgumentsCase('single constant argument',
                                                            source_elements=['the_argument'],
                                                            expected_resolved_values=lambda tcds: ['the_argument'],
                                                            expected_symbol_references=[])

        parser = sut.program_parser()
        parse_system_program.check_parsing_of_program(self,
                                                      parser,
                                                      pgm_args.system_program_argument_elements,
                                                      program_name_case,
                                                      arguments_case,
                                                      SymbolTable({}))


class TestParseSymbolReferenceProgram(unittest.TestCase):
    def test(self):
        # ARRANGE #

        cases = [
            NameAndValue('0 exit code',
                         0),
            NameAndValue('72 exit code',
                         72),
        ]
        for case in cases:
            with self.subTest(case.name):
                python_source = 'exit({exit_code})'.format(exit_code=case.value)

                sdv_of_referred_program = program_sdvs.for_py_source_on_command_line(python_source)

                program_that_executes_py_source = NameAndValue(
                    'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                    sdv_of_referred_program
                )

                symbols = SymbolTable({
                    program_that_executes_py_source.name:
                        symbol_utils.container(program_that_executes_py_source.value)
                })

                source = parse_source_of(
                    pgm_args.symbol_ref_command_line(sym_ref_args.sym_ref_cmd_line(
                        program_that_executes_py_source.name)))

                # ACT & ASSERT #
                pgm_exe_check.check(self,
                                    source,
                                    pgm_exe_check.Arrangement(
                                        symbols=symbols),
                                    pgm_exe_check.Expectation(
                                        symbol_references=asrt.matches_sequence([
                                            asrt_pgm.is_program_reference_to(program_that_executes_py_source.name),
                                        ]),
                                        result=pgm_exe_check.assert_process_result_data(
                                            exitcode=asrt.equals(case.value),
                                            stdout_contents=asrt.equals(''),
                                            stderr_contents=asrt.equals(''),
                                            contents_after_transformation=asrt.equals(''),
                                        )
                                    ))


class TestValidationOfProgramShouldIncludeValidationOfTransformer(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_symbol = NameAndValue('A_PROGRAM',
                                      program_sdvs.arbitrary_sdv__without_symbol_references())

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
                source = pgm_and_args_case.value.followed_by_lines(
                    [validation_case.value.transformer_arguments_elements]
                ).as_remaining_source

                symbols = symbol_table_from_name_and_sdvs([
                    program_symbol,
                    validation_case.value.symbol_context.name_and_sdv,
                ])

                with self.subTest(pgm_and_args_case=pgm_and_args_case.name,
                                  validation_case=validation_case.name):
                    # ACT & ASSERT #
                    pgm_exe_check.check(self,
                                        source,
                                        pgm_exe_check.Arrangement(
                                            symbols=symbols),
                                        pgm_exe_check.Expectation(
                                            symbol_references=asrt.anything_goes(),
                                            validation=validation_case.value.expectation,
                                            result=asrt.anything_goes(),
                                        ))


def parse_source_of(single_line: ArgumentElementsRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
