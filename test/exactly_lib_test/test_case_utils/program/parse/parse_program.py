import unittest

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.restrictions.test_resources import concrete_restriction_assertion as asrt_rr
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import program_execution_check as pgm_exe_check
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_case_utils.program.test_resources import sym_ref_cmd_line_args as sym_ref_args
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParseSymbolReferenceProgram)


class TestParseSymbolReferenceProgram(unittest.TestCase):
    def test(self):
        # ARRANGE #

        parser = sut.program_parser()

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
                                    parser,
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


def is_reference_data_type_symbol(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            asrt_rr.is_any_data_type_reference_restrictions())


def parse_source_of(single_line: ArgumentElementRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
