import unittest
from typing import List

from exactly_lib.impls.types.string_source import sdvs
from exactly_lib.impls.types.string_source import sdvs as str_src_sdvs
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    ExecutionExpectation, AssertionResolvingEnvironment, arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import \
    CHECKER_WO_EXECUTION
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import validation_cases
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources import abstract_syntaxes as str_abs_stx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as asrt_pgm_val
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_str_src


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulParsing),
        unittest.makeSuite(TestValidation),
    ])


class TestSuccessfulParsing(unittest.TestCase):
    def test_stdin_only_as_source_argument(self):
        # ARRANGE #
        str_src_contents = 'the_str_src_contents'
        stdin_syntax = str_src_abs_stx.StringSourceOfStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(str_src_contents)
        )

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            program_w_stdin = FullProgramAbsStx(
                pgm_and_args_case.pgm_and_args,
                stdin=stdin_syntax,
            )

            symbols = list(pgm_and_args_case.symbols)

            def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
                return asrt_pgm_val.matches_program(
                    asrt_command.matches_command(
                        driver=pgm_and_args_case.expected_command_driver(env),
                        arguments=asrt.is_empty_sequence
                    ),
                    stdin=asrt.matches_singleton_sequence(
                        asrt_str_src.matches__str(
                            asrt.equals(str_src_contents),
                        )
                    ),
                    transformer=asrt_pgm_val.is_no_transformation(),
                )

            with self.subTest(command=pgm_and_args_case.name):
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
                    )
                )

    def test_stdin_in_referenced_program_and_as_source_argument(self):
        # ARRANGE #
        str_src_contents__of_argument = 'the_str_src_contents__of_argument'
        str_src_contents__of_referenced_pgm = 'the_str_src_contents__of_program'
        stdin_argument_syntax = str_src_abs_stx.StringSourceOfStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(str_src_contents__of_argument)
        )
        stdin_sdv__of_referenced = str_src_sdvs.ConstantStringStringSourceSdv(
            string_sdvs.str_constant(str_src_contents__of_referenced_pgm)
        )

        referenced_program__system_program = 'the-system-program'
        referenced_program__sdv = program_sdvs.system_program(
            string_sdvs.str_constant(referenced_program__system_program),
            stdin=[stdin_sdv__of_referenced],
        )
        referenced_program = ProgramSymbolContext.of_sdv('REFERENCED_PROGRAM',
                                                         referenced_program__sdv)

        symbols__symbol_table = [referenced_program]
        symbols__expected_references = [referenced_program]

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
                program_w_stdin = FullProgramAbsStx(
                    ProgramOfSymbolReferenceAbsStx(
                        referenced_program.name,
                        [ArgumentOfStringAbsStx.of_str(arg) for arg in arguments_case.value]
                    ),
                    stdin=stdin_argument_syntax,
                )

                expected_primitive = asrt_pgm_val.matches_program(
                    asrt_command.matches_command(
                        driver=asrt_command.matches_system_program_command_driver(
                            asrt.equals(referenced_program__system_program)
                        ),
                        arguments=asrt.equals(arguments_case.value),
                    ),
                    stdin=asrt.matches_sequence([
                        asrt_str_src.matches__str(asrt.equals(str_src_contents__of_referenced_pgm)),
                        asrt_str_src.matches__str(asrt.equals(str_src_contents__of_argument)),
                    ]),
                    transformer=asrt_pgm_val.is_no_transformation(),
                )

                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    program_w_stdin,
                    arrangement_w_tcds(
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
                 sdv_of_referenced_program: sdvs.StringSourceSdv,
                 syntax_accumulated: StringSourceAbsStx,
                 symbols: List[SymbolContext],
                 ):
        self.name = name
        self.sdv_of_referenced_program = sdv_of_referenced_program
        self.syntax_of_accumulated = syntax_accumulated
        self.symbols = symbols


class TestValidation(unittest.TestCase):
    def test_stdin_only_as_source_argument(self):
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            for validation_case in validation_cases.failing_validation_cases():
                program_w_stdin = FullProgramAbsStx(
                    pgm_and_args_case.pgm_and_args,
                    stdin=validation_case.value.syntax,
                )

                symbols = list(pgm_and_args_case.symbols) + [validation_case.value.symbol_context]

                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    program_w_stdin,
                    pgm_and_args_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                    MultiSourceExpectation.of_const(
                        symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                        execution=ExecutionExpectation(
                            validation=validation_case.value.assertion,
                        ),
                        primitive=asrt.anything_goes(),
                    ),
                    sub_test_identifiers={
                        'command': pgm_and_args_case.name,
                        'validation': validation_case.name
                    },
                )

    def test_stdin_in_referenced_program_and_as_source_argument(self):
        # ARRANGE #
        stdin_contents = 'str_src_contents'
        valid_stdin_sdv = sdvs.ConstantStringStringSourceSdv(
            string_sdvs.str_constant(stdin_contents)
        )
        valid_stdin_syntax = str_src_abs_stx.StringSourceOfStringAbsStx(
            str_abs_stx.StringLiteralAbsStx(stdin_contents)
        )

        referenced_program__system_program = 'the-system-program'

        for validation_case in validation_cases.failing_validation_cases():
            invalid_stdin_location_cases = [
                ValidationCaseWAccumulation(
                    'in referenced symbol',
                    sdv_of_referenced_program=validation_case.value.symbol_context.sdv,
                    syntax_accumulated=valid_stdin_syntax,
                    symbols=[],
                ),
                ValidationCaseWAccumulation(
                    'as source argument',
                    sdv_of_referenced_program=valid_stdin_sdv,
                    syntax_accumulated=validation_case.value.syntax,
                    symbols=[validation_case.value.symbol_context],
                ),
            ]
            for invalid_stdin_location_case in invalid_stdin_location_cases:
                referenced_program__sdv = program_sdvs.system_program(
                    string_sdvs.str_constant(referenced_program__system_program),
                    stdin=[invalid_stdin_location_case.sdv_of_referenced_program]
                )
                referenced_program = ProgramSymbolContext.of_sdv('REFERENCED_PROGRAM',
                                                                 referenced_program__sdv)
                program_w_stdin = FullProgramAbsStx(
                    ProgramOfSymbolReferenceAbsStx(
                        referenced_program.name,
                    ),
                    stdin=invalid_stdin_location_case.syntax_of_accumulated,
                )
                symbols__all = [validation_case.value.symbol_context, referenced_program]
                symbols__expected_references = [referenced_program] + invalid_stdin_location_case.symbols

                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    program_w_stdin,
                    arrangement_w_tcds(
                        symbols=SymbolContext.symbol_table_of_contexts(symbols__all),
                    ),
                    MultiSourceExpectation.of_const(
                        symbol_references=SymbolContext.references_assertion_of_contexts(
                            symbols__expected_references
                        ),
                        execution=ExecutionExpectation(
                            validation=validation_case.value.assertion,
                        ),
                        primitive=asrt.anything_goes(),
                    ),
                    sub_test_identifiers={
                        'validation': validation_case.name,
                        'invalid_stdin_location': invalid_stdin_location_case.name,
                    }
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
