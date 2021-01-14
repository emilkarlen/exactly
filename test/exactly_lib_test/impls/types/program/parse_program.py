import unittest

from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation, \
    Expectation, MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc, \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.test_resources import integration_check_applier
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.impls.types.program.test_resources import pgm_and_args_cases
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import PgmAndArgsWArgumentsAbsStx, \
    FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentOfStringAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerCompositionAbsStx, CustomStringTransformerAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestJustPgmAndArgs(),
        TestArguments(),
        TestPgmAndArgsFollowedByTransformation(),
        TestTransformerShouldBeParsedAsSimpleExpression(),
    ])


class TestJustPgmAndArgs(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list():
            with self.subTest(command=pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    pgm_and_args_case.pgm_and_args,
                    pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(pgm_and_args_case.symbols)),
                    MultiSourceExpectation(
                        symbol_references=SymbolContext.references_assertion_of_contexts(pgm_and_args_case.symbols),
                        primitive=lambda env: (
                            asrt_pgm_val.matches_program(
                                asrt_command.matches_command(
                                    driver=pgm_and_args_case.expected_command_driver(env),
                                    arguments=asrt.is_empty_sequence
                                ),
                                stdin=asrt_pgm_val.is_no_stdin(),
                                transformer=asrt_pgm_val.is_no_transformation(),
                            )
                        )
                    )
                )


class TestArguments(unittest.TestCase):
    def runTest(self):
        arg_wo_space = 'arg_wo_space'
        arg_w_space = 'an arg w space'
        arguments_cases = [
            NIE(
                'one',
                input_value=[ArgumentOfStringAbsStx.of_str(arg_w_space, QuoteType.SOFT)],
                expected_value=[arg_w_space],
            ),
            NIE(
                'two',
                input_value=[ArgumentOfStringAbsStx.of_str(arg_wo_space),
                             ArgumentOfStringAbsStx.of_str(arg_w_space, QuoteType.SOFT)],
                expected_value=[arg_wo_space, arg_w_space],
            ),
        ]
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases__w_argument_list():
            for arguments_case in arguments_cases:
                pgm_w_args = PgmAndArgsWArgumentsAbsStx(pgm_and_args_case.pgm_and_args,
                                                        arguments_case.input_value)
                expected_arguments = asrt.matches_sequence([
                    asrt.equals(arg)
                    for arg in arguments_case.expected_value
                ])
                expectation = MultiSourceExpectation(
                    symbol_references=SymbolContext.references_assertion_of_contexts(pgm_and_args_case.symbols),
                    primitive=lambda env: (
                        asrt_pgm_val.matches_program(
                            asrt_command.matches_command(driver=pgm_and_args_case.expected_command_driver(env),
                                                         arguments=expected_arguments),
                            stdin=asrt_pgm_val.is_no_stdin(),
                            transformer=asrt_pgm_val.is_no_transformation(),
                        ))
                )
                with self.subTest(command=pgm_and_args_case.name,
                                  arguments=arguments_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                        pgm_w_args,
                        pgm_and_args_case.mk_arrangement(
                            SymbolContext.symbol_table_of_contexts(pgm_and_args_case.symbols)),
                        expectation,
                    )


class TestPgmAndArgsFollowedByTransformation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        transformer = StringTransformerPrimitiveSymbolContext(
            'STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list():
            program_w_transformer = FullProgramAbsStx(
                pgm_and_args_case.pgm_and_args,
                transformation=transformer.abs_stx_of_reference
            )

            symbols = list(pgm_and_args_case.symbols) + [transformer]

            with self.subTest(command=pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    program_w_transformer,
                    pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                    MultiSourceExpectation(
                        symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                        primitive=lambda env: (
                            asrt_pgm_val.matches_program(
                                asrt_command.matches_command(
                                    driver=pgm_and_args_case.expected_command_driver(env),
                                    arguments=asrt.is_empty_sequence
                                ),
                                stdin=asrt_pgm_val.is_no_stdin(),
                                transformer=asrt.matches_singleton_sequence(asrt.is_(transformer.primitive)),
                            )
                        )
                    )
                )


class TestTransformerShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        transformer = StringTransformerPrimitiveSymbolContext(
            'STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )
        after_bin_op = 'after bin op'
        after_bin_op_syntax = CustomStringTransformerAbsStx.of_str(after_bin_op)
        composition_string_transformer = StringTransformerCompositionAbsStx(
            [transformer.abs_stx_of_reference, after_bin_op_syntax],
            within_parens=False,
            allow_elements_on_separate_lines=False,
        )
        expected_source_after_parse = asrt_source.is_at_line(
            current_line_number=2,
            remaining_part_of_current_line=' '.join([composition_string_transformer.operator_name(),
                                                     after_bin_op]),
        )
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list():
            command_followed_by_transformer = FullProgramAbsStx(
                pgm_and_args_case.pgm_and_args,
                transformation=composition_string_transformer,
            )
            symbols = list(pgm_and_args_case.symbols) + [transformer]

            with self.subTest(command=pgm_and_args_case.name):
                source = remaining_source(
                    command_followed_by_transformer.tokenization().layout(LayoutSpec.of_default())
                )
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check(
                    self,
                    source,
                    None,
                    pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                    Expectation(
                        ParseExpectation(
                            source=expected_source_after_parse,
                            symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                        ),
                        primitive=lambda env: (
                            asrt_pgm_val.matches_program(
                                asrt_command.matches_command(
                                    driver=pgm_and_args_case.expected_command_driver(env),
                                    arguments=asrt.is_empty_sequence
                                ),
                                stdin=asrt_pgm_val.is_no_stdin(),
                                transformer=asrt.matches_singleton_sequence(asrt.is_(transformer.primitive)),
                            )
                        )
                    )
                )


CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    parse_program.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        integration_check_applier.NullApplier(),
    ),
    True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
