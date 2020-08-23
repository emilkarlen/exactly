import unittest
from pathlib import PurePosixPath

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.files_condition import files_conditions
from exactly_lib.test_case_utils.files_condition import parse as sut
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.symbol.test_resources.files_condition import FilesConditionSymbolContext, \
    is_reference_to_files_condition
from exactly_lib_test.test_case_utils.expression.test_resources.syntax_cases import TestCaseGeneratorForParenthesis
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_condition.test_resources import primitive_assertions as asrt_primitive
from exactly_lib_test.test_case_utils.files_condition.test_resources.integration_check import CHECKER
from exactly_lib_test.test_case_utils.files_condition.test_resources.validation_cases import \
    failing_validation_cases__multi_exe
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, prim_asrt__constant
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParenthesisSyntax)


class TestParenthesisSyntax(unittest.TestCase):
    def test_parse_SHOULD_fail_WHEN_syntax_is_invalid(self):
        # ARRANGE #
        case_generator = TestCaseGeneratorForParenthesis(
            symbol_syntax.A_VALID_SYMBOL_NAME,
            symbol_syntax.NOT_A_VALID_SYMBOL_NAME_NOR_PRIMITIVE_GRAMMAR_ELEMENT_NAME,
        )
        for case in case_generator.parse_should_fail_when_syntax_is_invalid():
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parsers().full.parse(case.value)

    def test_expression_inside_parentheses_SHOULD_be_validated(self):
        symbol_name = 'fc_symbol'
        CHECKER.check_multi__w_source_variants(
            self,
            arguments=args.Parentheses(args.SymbolReferenceWReferenceSyntax(symbol_name)).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(is_reference_to_files_condition(symbol_name)),
            input_=None,
            execution=failing_validation_cases__multi_exe(symbol_name),
        )

    def test_expression_inside_parentheses_SHOULD_be_equal_to_expression_inside_parentheses(self):
        # ARRANGE #
        file_name = 'the-file-name'
        referenced_sdv = files_conditions.new_constant([
            (string_sdvs.str_constant(file_name), None)
        ])
        expected = asrt_primitive.files_matches({
            PurePosixPath(file_name): asrt.is_none
        })
        symbol = FilesConditionSymbolContext.of_sdv(
            'fc_symbol',
            referenced_sdv
        )
        source = args.Parentheses(args.SymbolReferenceWReferenceSyntax(symbol.name))
        # ACT & ASSERT #
        CHECKER.check__w_source_variants(
            self,
            source.as_arguments,
            None,
            arrangement_wo_tcds(symbol.symbol_table),
            Expectation(
                ParseExpectation(
                    symbol_references=symbol.references_assertion
                ),
                ExecutionExpectation(),
                prim_asrt__constant(expected)
            )
        )


STRING_SYMBOL_NAME = 'a_valid_symbol_name__string'
FILE_MATCHER_SYMBOL_NAME = 'a_valid_symbol_name__file_matcher'

STRING_SYMBOL_NAME_2 = 'a_valid_symbol_name__string_2'
FILE_MATCHER_SYMBOL_NAME_2 = 'a_valid_symbol_name__file_matcher_2'
