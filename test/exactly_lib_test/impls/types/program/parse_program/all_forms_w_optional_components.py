import unittest

from exactly_lib.type_val_prims.program.program import Program
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    AssertionResolvingEnvironment, arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import \
    CHECKER_WO_EXECUTION
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx, \
    PgmAndArgsWArgumentsAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as asrt_pgm_val
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_str_src
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestPgmAndArgs(),
        TestShellCommandLine(),
    ])


class TestPgmAndArgs(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        arguments = ['arg']
        str_src_contents = 'the_str_src_contents'
        stdin_syntax = str_src_abs_stx.StringSourceWithinParensAbsStx(
            str_src_abs_stx.StringSourceOfStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(str_src_contents)
            )
        )
        transformer_symbol = StringTransformerPrimitiveSymbolContext(
            'TRANSFORMER',
            string_transformers.to_uppercase()
        )

        for pgm_and_args_case in pgm_and_args_cases.cases__w_argument_list__including_program_reference():
            program_w_stdin = FullProgramAbsStx(
                PgmAndArgsWArgumentsAbsStx(
                    pgm_and_args_case.pgm_and_args,
                    [ArgumentOfStringAbsStx.of_str(arg) for arg in arguments],
                ),
                stdin=stdin_syntax,
                transformation=transformer_symbol.abstract_syntax,
            )

            symbols = list(pgm_and_args_case.symbols) + [transformer_symbol]

            def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
                return asrt_pgm_val.matches_program(
                    asrt_command.matches_command(
                        driver=pgm_and_args_case.expected_command_driver(env),
                        arguments=asrt.equals(arguments),
                    ),
                    stdin=asrt.matches_singleton_sequence(
                        asrt_str_src.matches__str(
                            asrt.equals(str_src_contents),
                        )
                    ),
                    transformer=asrt.matches_singleton_sequence(
                        asrt.is_(transformer_symbol.primitive)
                    ),
                )

            # ACT & ASSERT #
            CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                self,
                equivalent_source_variants__for_expr_parse__s__nsc,
                program_w_stdin,
                arrangement_w_tcds(
                    symbols=SymbolContext.symbol_table_of_contexts(symbols),
                    tcds_contents=pgm_and_args_case.tcds,
                ),
                MultiSourceExpectation(
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                    primitive=expected_program,
                ),
                sub_test_identifiers={
                    'command': pgm_and_args_case.name
                }
            )


class TestShellCommandLine(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        str_src_contents = 'the_str_src_contents'
        stdin_syntax = str_src_abs_stx.StringSourceWithinParensAbsStx(
            str_src_abs_stx.StringSourceOfStringAbsStx(
                str_abs_stx.StringLiteralAbsStx(str_src_contents)
            )
        )
        transformer_symbol = StringTransformerPrimitiveSymbolContext(
            'TRANSFORMER',
            string_transformers.to_uppercase()
        )

        pgm_and_args_case = pgm_and_args_cases.shell()

        program_w_stdin = FullProgramAbsStx(
            pgm_and_args_case.pgm_and_args,
            stdin=stdin_syntax,
            transformation=transformer_symbol.abstract_syntax,
        )

        symbols = list(pgm_and_args_case.symbols) + [transformer_symbol]

        def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
            return asrt_pgm_val.matches_program(
                asrt_command.matches_command(
                    driver=pgm_and_args_case.expected_command_driver(env),
                    arguments=asrt.is_empty_sequence,
                ),
                stdin=asrt.matches_singleton_sequence(
                    asrt_str_src.matches__str(
                        asrt.equals(str_src_contents),
                    )
                ),
                transformer=asrt.matches_singleton_sequence(
                    asrt.is_(transformer_symbol.primitive)
                ),
            )

        # ACT & ASSERT #
        s = program_w_stdin.as_str__default()
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_expr_parse__s__nsc,
            program_w_stdin,
            arrangement_w_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
                tcds_contents=pgm_and_args_case.tcds,
            ),
            MultiSourceExpectation(
                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                primitive=expected_program,
            )
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
