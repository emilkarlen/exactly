import unittest
from typing import List

from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import ParseExpectation, \
    Expectation, MultiSourceExpectation, arrangement_wo_tcds, ExecutionExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import CHECKER_WO_EXECUTION
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_transformer.test_resources import validation_cases
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import \
    StringTransformerCompositionAbsStx, CustomStringTransformerAbsStx
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext, StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as asrt_pgm_val
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParsingAndSymbolReferences),
        unittest.makeSuite(TestValidation),
        TestTransformerShouldBeParsedAsSimpleExpression(),
    ])


class TestParsingAndSymbolReferences(unittest.TestCase):
    def test_transformation_only_as_source_argument(self):
        # ARRANGE #
        transformer = StringTransformerPrimitiveSymbolContext(
            'STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            program_w_transformer = FullProgramAbsStx(
                pgm_and_args_case.pgm_and_args,
                transformation=transformer.abstract_syntax
            )

            symbols = list(pgm_and_args_case.symbols) + [transformer]

            with self.subTest(command=pgm_and_args_case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
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

    def test_transformation_in_referenced_program_and_as_source_argument(self):
        # ARRANGE #
        transformer__in_referenced_program = StringTransformerPrimitiveSymbolContext(
            'TRANSFORMER_IN_REFERENCED_PROGRAM',
            string_transformers.delete_everything()
        )
        referenced_program__system_program = 'the-system-program'
        referenced_program__sdv = program_sdvs.system_program(
            string_sdvs.str_constant(referenced_program__system_program),
            transformations=[transformer__in_referenced_program.reference_sdv]
        )
        referenced_program = ProgramSymbolContext.of_sdv('REFERENCED_PROGRAM',
                                                         referenced_program__sdv)

        transformer__in_source = StringTransformerPrimitiveSymbolContext(
            'TRANSFORMER_IN_SOURCE',
            string_transformers.to_uppercase()
        )
        symbols__symbol_table = [referenced_program,
                                 transformer__in_referenced_program,
                                 transformer__in_source]
        symbols__expected_references = [referenced_program,
                                        transformer__in_source]

        arguments_cases = [
            NameAndValue(
                'no arguments',
                [],
            ),
            NameAndValue(
                'single argument',
                ['arg1'],
            )
        ]

        for arguments_case in arguments_cases:
            with self.subTest(arguments=arguments_case.name):
                program_w_transformer = FullProgramAbsStx(
                    ProgramOfSymbolReferenceAbsStx(
                        referenced_program.name,
                        [ArgumentOfStringAbsStx.of_str(arg) for arg in arguments_case.value]
                    ),
                    transformation=transformer__in_source.abstract_syntax
                )

                expected_primitive = asrt_pgm_val.matches_program(
                    asrt_command.matches_command(
                        driver=asrt_command.matches_system_program_command_driver(
                            asrt.equals(referenced_program__system_program)
                        ),
                        arguments=asrt.equals(arguments_case.value),
                    ),
                    stdin=asrt_pgm_val.is_no_stdin(),
                    transformer=asrt.matches_sequence([
                        asrt.is_(transformer__in_referenced_program.primitive),
                        asrt.is_(transformer__in_source.primitive),
                    ]),
                )

                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    program_w_transformer,
                    arrangement_wo_tcds(
                        symbols=SymbolContext.symbol_table_of_contexts(symbols__symbol_table),
                    ),
                    MultiSourceExpectation.of_const(
                        symbol_references=SymbolContext.references_assertion_of_contexts(
                            symbols__expected_references
                        ),
                        primitive=expected_primitive,
                    )
                )


class ValidationCaseWAccumulation:
    def __init__(self,
                 name: str,
                 of_referenced_program: StringTransformerSymbolContext,
                 accumulated: StringTransformerSymbolContext,
                 ):
        self.name = name
        self.of_referenced_program = of_referenced_program
        self.accumulated = accumulated

    def all_symbols(self) -> List[SymbolContext]:
        return [self.of_referenced_program, self.accumulated]


class TestValidation(unittest.TestCase):
    def test_transformation_only_as_source_argument(self):
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            for validation_case in validation_cases.failing_validation_cases():
                program_w_transformer = FullProgramAbsStx(
                    pgm_and_args_case.pgm_and_args,
                    transformation=validation_case.value.symbol_context.abstract_syntax,
                )

                symbols = list(pgm_and_args_case.symbols) + [validation_case.value.symbol_context]

                with self.subTest(command=pgm_and_args_case.name,
                                  validation=validation_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_expr_parse__s__nsc,
                        program_w_transformer,
                        pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                        MultiSourceExpectation.of_const(
                            symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                            execution=ExecutionExpectation(
                                validation=validation_case.value.expectation,
                            ),
                            primitive=asrt.anything_goes(),
                        )
                    )

    def test_transformation_in_referenced_program_and_as_source_argument(self):
        # ARRANGE #
        valid_transformer = StringTransformerSymbolContext.of_arbitrary_value(
            'VALID_TRANSFORMER',
        )

        referenced_program__system_program = 'the-system-program'

        for validation_case in validation_cases.failing_validation_cases('INVALID_TRANSFORMER'):
            invalid_transformer_location_cases = [
                ValidationCaseWAccumulation(
                    'in referenced program',
                    of_referenced_program=validation_case.value.symbol_context,
                    accumulated=valid_transformer,
                ),
                ValidationCaseWAccumulation(
                    'in referenced program',
                    of_referenced_program=valid_transformer,
                    accumulated=validation_case.value.symbol_context,
                ),
            ]
            for invalid_transformer_location_case in invalid_transformer_location_cases:
                referenced_program__sdv = program_sdvs.system_program(
                    string_sdvs.str_constant(referenced_program__system_program),
                    transformations=[invalid_transformer_location_case.of_referenced_program.reference_sdv]
                )
                referenced_program = ProgramSymbolContext.of_sdv('REFERENCED_PROGRAM',
                                                                 referenced_program__sdv)
                program_w_transformer = FullProgramAbsStx(
                    ProgramOfSymbolReferenceAbsStx(
                        referenced_program.name,
                    ),
                    transformation=invalid_transformer_location_case.accumulated.abstract_syntax,
                )
                symbols__all = [referenced_program,
                                valid_transformer,
                                validation_case.value.symbol_context,
                                ]
                symbols__expected_references = [referenced_program,
                                                invalid_transformer_location_case.accumulated]

                with self.subTest(validation=validation_case.name,
                                  invalid_transformer_location=invalid_transformer_location_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_expr_parse__s__nsc,
                        program_w_transformer,
                        arrangement_wo_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(symbols__all),
                        ),
                        MultiSourceExpectation.of_const(
                            symbol_references=SymbolContext.references_assertion_of_contexts(
                                symbols__expected_references
                            ),
                            execution=ExecutionExpectation(
                                validation=validation_case.value.expectation,
                            ),
                            primitive=asrt.anything_goes(),
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
            [transformer.abstract_syntax, after_bin_op_syntax],
            within_parens=False,
            allow_elements_on_separate_lines=False,
        )
        expected_source_after_parse = asrt_source.is_at_line(
            current_line_number=2,
            remaining_part_of_current_line=' '.join([composition_string_transformer.operator_name(),
                                                     after_bin_op]),
        )
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
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


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
