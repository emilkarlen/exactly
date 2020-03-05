import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.symbol.test_resources import line_matcher
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.symbol.test_resources.symbol_utils import symbol_table_from_name_and_sdvs
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_arg
from exactly_lib_test.test_case_utils.line_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.logic.test_resources import integration_check as logic_integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_wo_tcds
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as st_args, \
    model_construction
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution, StExpectation
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.values import is_identical_to, \
    line_matcher_from_predicates


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestSelectTransformer),
        unittest.makeSuite(TestLineMatcherPrimitive),
        ValidatorShouldValidateLineMatcher(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'no arguments',
                st_args.syntax_for_select_transformer(''),
            ),
            NameAndValue(
                'argument is not a line matcher',
                st_args.syntax_for_select_transformer(symbol_syntax.NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parser().parse(parse_source.remaining_source(case.value))


class TestSelectTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        # ARRANGE #

        matcher = NameAndValue(
            'line_matcher_symbol',
            LineMatcherStv(
                matchers.sdv_from_primitive_value(
                    matchers.MatcherWithConstantResult(False)
                )
            ),
        )
        line_matcher_arg = lm_arg.SymbolReference(matcher.name)

        arguments = st_args.syntax_for_select_transformer(str(line_matcher_arg))

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            Arguments(arguments),
            model_construction.of_lines([]),
            arrangement_wo_tcds(
                symbols=symbol_table_from_name_and_sdvs([
                    matcher,
                ])
            ),
            expectation_of_successful_execution(
                symbol_references=asrt.matches_singleton_sequence(
                    line_matcher.is_line_matcher_reference_to__ref(matcher.name)
                ),
                output_lines=[],
                is_identity_transformer=False,
            )
        )

    def test_every_line_SHOULD_be_filtered(self):
        matcher = NameAndValue(
            'line_matcher_symbol',
            line_matcher.stv_from_primitive_value(
                sub_string_line_matcher('MATCH'),
            ),
        )
        line_matcher_arg = lm_arg.SymbolReference(matcher.name)
        cases = [
            NEA('no lines',
                [],
                [],
                ),
            NEA('single line that matches',
                ['a MATCH'],
                ['a MATCH'],
                ),
            NEA('single line that does not match',
                actual=['not a match'],
                expected=[],
                ),
            NEA('some lines matches',
                actual=[
                    'first line is a MATCH',
                    'second line is not a match',
                    'third line MATCH:es',
                    'fourth line not',
                ],
                expected=[
                    'first line is a MATCH',
                    'third line MATCH:es',
                ],
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                arguments = st_args.syntax_for_select_transformer(str(line_matcher_arg))
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(case.actual),
                    arrangement_wo_tcds(
                        symbols=symbol_table_from_name_and_sdvs([
                            matcher,
                        ])
                    ),
                    expectation_of_successful_filter_execution(
                        output_lines=case.expected,
                        symbol_references=asrt.matches_singleton_sequence(
                            line_matcher.is_line_matcher_reference_to__ref(matcher.name)
                        ),
                    )
                )

    def test_other_scenarios(self):
        cases = [
            NameAndValue(
                'trailing new lines should be removed from line matcher model, but not from transformer output',
                (line_matcher_from_predicates(line_contents_predicate=lambda x: x == 'X'),
                 ['X\n'],
                 ['X\n'])
            ),
            NameAndValue(
                'line numbers should be paired with lines in order of iterator (1)',
                (is_identical_to(1, 'i'),
                 ['i',
                  'ii'],
                 ['i'])
            ),
            NameAndValue(
                'line numbers should be paired with lines in order of iterator (2)',
                (is_identical_to(2, 'ii'),
                 ['i',
                  'ii'],
                 ['ii'])
            ),
            NameAndValue(
                'line numbers should be propagated to line matcher',
                (line_matcher_from_predicates(line_num_predicate=lambda x: x in {1, 3}),
                 [
                     'i',
                     'ii',
                     'iii',
                     'iv',
                 ],
                 [
                     'i',
                     'iii',
                 ])
            ),
        ]
        line_matcher_name = 'the_line_matcher_symbol_name'
        line_matcher_arg = lm_arg.SymbolReference(line_matcher_name)
        arguments = st_args.syntax_for_select_transformer(str(line_matcher_arg))

        for case in cases:
            matcher, input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                # ACT & ASSERT #

                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(input_lines),
                    arrangement_wo_tcds(
                        symbols=symbol_table_from_name_and_sdvs([
                            NameAndValue(line_matcher_name,
                                         line_matcher.stv_from_primitive_value(
                                             matcher,
                                         ),
                                         ),
                        ])
                    ),
                    expectation_of_successful_filter_execution(
                        output_lines=expected_output_lines,
                        symbol_references=asrt.matches_singleton_sequence(
                            line_matcher.is_line_matcher_reference_to__ref(line_matcher_name)
                        )
                    )
                )


class TestLineMatcherPrimitive(unittest.TestCase):
    def test(self):
        # ARRANGE #

        reg_ex_pattern = 'const_pattern'
        arguments = st_args.syntax_for_select_transformer(str(lm_arg.Matches(reg_ex_pattern)))

        lines = [
            reg_ex_pattern,
            'non matching line',
        ]
        expected_lines = [
            reg_ex_pattern,
        ]

        # ACT & ASSERT #

        integration_check.CHECKER.check__w_source_variants(
            self,
            Arguments(arguments),
            model_construction.of_lines(lines),
            arrangement_wo_tcds(),
            expectation_of_successful_filter_execution(
                output_lines=expected_lines,
                symbol_references=asrt.is_empty_sequence,
            )
        )


class ValidatorShouldValidateLineMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for case in validation_cases.failing_validation_cases():
            line_matcher_symbol_context = case.value.symbol_context
            line_matcher_arg = lm_arg.SymbolReference(line_matcher_symbol_context.name)

            arguments = st_args.syntax_for_select_transformer(str(line_matcher_arg))

            with self.subTest(case.name):
                # ACT & ASSERT #
                integration_check.CHECKER.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines([]),
                    arrangement_wo_tcds(
                        symbols=line_matcher_symbol_context.symbol_table
                    ),
                    logic_integration_check.Expectation(
                        logic_integration_check.ParseExpectation(
                            symbol_references=line_matcher_symbol_context.references_assertion
                        ),
                        logic_integration_check.ExecutionExpectation(
                            validation=case.value.expectation,
                        )
                    )
                )


def sub_string_line_matcher(sub_string: str) -> LineMatcher:
    return line_matcher_from_predicates(line_contents_predicate=lambda actual: sub_string in actual)


def expectation_of_successful_filter_execution(output_lines: List[str],
                                               symbol_references: ValueAssertion[Sequence[SymbolReference]],
                                               ) -> StExpectation:
    return integration_check.expectation_of_successful_execution(
        output_lines,
        symbol_references,
        False,
    )
