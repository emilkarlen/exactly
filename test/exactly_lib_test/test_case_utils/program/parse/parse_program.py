import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.parse import parse_system_program
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_execution_check as pgm_exe_check
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSymbolReferenceProgram),
        unittest.makeSuite(TestParseSystemProgram),

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
        arguments_case = parse_system_program.ArgumentsCase(
            'single constant argument',
            source_elements=['the_argument'],
            expected_dir_dependencies=set(),
            expected_resolved_values=lambda tcds: ['the_argument'],
            expected_symbol_references=[],
        )

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

                resolver_of_referred_program = program_resolvers.for_py_source_on_command_line(python_source)

                program_that_executes_py_source = NameAndValue(
                    'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                    resolver_of_referred_program
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


def parse_source_of(single_line: ArgumentElementRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
