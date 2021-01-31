import unittest

from exactly_lib.impls.types.program.parse import parse_program as sut
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    AssertionResolvingEnvironment, arrangement_wo_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import \
    CHECKER_WO_EXECUTION
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.abstract_syntax_impls import WithinParensAbsStx, OptionallyOnNewLine, \
    CustomAbsStx
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as asrt_pgm_val


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidSyntax(),
        unittest.makeSuite(TestInvalidSyntax),
    ])


class TestValidSyntax(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_ref_case = pgm_and_args_cases.program_reference__w_argument_list()

        def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
            return asrt_pgm_val.matches_program(
                asrt_command.matches_command(
                    driver=program_ref_case.expected_command_driver(env),
                    arguments=asrt.is_empty_sequence,
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_expr_parse__s__nsc,
            OptionallyOnNewLine(WithinParensAbsStx(program_ref_case.pgm_and_args,
                                                   end_paren_on_separate_line=True)),
            arrangement_wo_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(program_ref_case.symbols),
            ),
            MultiSourceExpectation(
                symbol_references=SymbolContext.references_assertion_of_contexts(program_ref_case.symbols),
                primitive=expected_program,
            )
        )


class TestInvalidSyntax(unittest.TestCase):
    def test_fail_when_missing_end_end_paren(self):
        # ARRANGE #
        valid_program = ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL')
        missing_end_paren = CustomAbsStx(
            TokenSequence.concat([
                TokenSequence.singleton('('),
                valid_program.tokenization(),
            ])
        )
        # ACT & ASSERT #
        PARSE_CHECKER.check_invalid_syntax__abs_stx(
            self,
            OptionallyOnNewLine(missing_end_paren)
        )


PARSE_CHECKER = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
