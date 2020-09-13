import unittest
from typing import List, Sequence

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer as sut
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import line_matcher
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherSymbolContext, \
    LineMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_arg
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_args
from exactly_lib_test.test_case_utils.line_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation
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
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
        unittest.makeSuite(TestFiltering),
        unittest.makeSuite(TestLineMatcherPrimitive),
        ValidatorShouldValidateLineMatcher(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'no arguments',
                st_args.syntax_for_filter_transformer(''),
            ),
            NameAndValue(
                'argument is not a line matcher',
                st_args.syntax_for_filter_transformer(symbol_syntax.NOT_A_VALID_SYMBOL_NAME),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parsers(True).full.parse(parse_source.remaining_source(case.value))


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        model = ['the line']
        line_matcher__constant_false = LineMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER',
            False,
        )
        after_bin_op = 'after bin op'
        lm_argument = lm_args.And([
            lm_args.SymbolReference(line_matcher__constant_false.name),
            lm_args.Custom(after_bin_op),
        ])
        arguments = st_args.syntax_for_filter_transformer(lm_argument.as_str)

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=remaining_source(arguments),
            input_=model_construction.of_lines(model),
            arrangement=arrangement_w_tcds(
                symbols=line_matcher__constant_false.symbol_table,
            ),
            expectation=expectation_of_successful_execution(
                source=asrt_source.is_at_line(
                    current_line_number=1,
                    remaining_part_of_current_line=lm_argument.operator_name + ' ' + after_bin_op,
                ),
                symbol_references=line_matcher__constant_false.references_assertion,
                output_lines=[],
                is_identity_transformer=False,
            )
        )


class TestFiltering(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        # ARRANGE #

        matcher = LineMatcherSymbolContext.of_primitive_constant(
            'line_matcher_symbol',
            False,
        )
        line_matcher_arg = lm_arg.SymbolReference(matcher.name)

        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            Arguments(arguments),
            model_construction.of_lines([]),
            arrangement_w_tcds(
                symbols=matcher.symbol_table
            ),
            expectation_of_successful_execution(
                symbol_references=asrt.matches_singleton_sequence(
                    matcher.reference_assertion
                ),
                output_lines=[],
                is_identity_transformer=False,
            )
        )

    def test_every_line_SHOULD_be_filtered(self):
        matcher = LineMatcherSymbolContext.of_primitive(
            'line_matcher_symbol',
            sub_string_line_matcher('MATCH'),
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
                actual=with_appended_new_lines([
                    'first line is a MATCH',
                    'second line is not a match',
                    'third line MATCH:es',
                    'fourth line not',
                ]),
                expected=with_appended_new_lines([
                    'first line is a MATCH',
                    'third line MATCH:es',
                ]),
                ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name):
                arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(case.actual),
                    arrangement_w_tcds(
                        symbols=matcher.symbol_table
                    ),
                    expectation_of_successful_filter_execution(
                        output_lines=case.expected,
                        symbol_references=asrt.matches_singleton_sequence(
                            line_matcher.is_reference_to_line_matcher(matcher.name)
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
                 with_appended_new_lines([
                     'i',
                     'ii',
                 ]),
                 with_appended_new_lines(['i'])
                 )
            ),
            NameAndValue(
                'line numbers should be paired with lines in order of iterator (2)',
                (is_identical_to(2, 'ii'),
                 with_appended_new_lines([
                     'i',
                     'ii',
                 ]),
                 with_appended_new_lines(['ii'])
                 )
            ),
            NameAndValue(
                'line numbers should be propagated to line matcher',
                (line_matcher_from_predicates(line_num_predicate=lambda x: x in {1, 3}),
                 with_appended_new_lines([
                     'i',
                     'ii',
                     'iii',
                     'iv',
                 ]),
                 with_appended_new_lines([
                     'i',
                     'iii',
                 ])
                 )
            ),
        ]
        line_matcher_name = 'the_line_matcher_symbol_name'
        line_matcher_arg = lm_arg.SymbolReference(line_matcher_name)
        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

        for case in cases:
            matcher, input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                # ACT & ASSERT #

                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines(input_lines),
                    arrangement_w_tcds(
                        symbols=LineMatcherSymbolContext.of_primitive(
                            line_matcher_name,
                            matcher,
                        ).symbol_table,
                    ),
                    expectation_of_successful_filter_execution(
                        output_lines=expected_output_lines,
                        symbol_references=asrt.matches_singleton_sequence(
                            line_matcher.is_reference_to_line_matcher(line_matcher_name)
                        )
                    )
                )


class TestLineMatcherPrimitive(unittest.TestCase):
    def test(self):
        # ARRANGE #

        reg_ex_pattern = 'const_pattern'
        arguments = st_args.syntax_for_filter_transformer(str(lm_arg.Matches(reg_ex_pattern)))

        lines = [
            reg_ex_pattern,
            'non matching line',
        ]
        expected_lines = [
            reg_ex_pattern,
        ]

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            Arguments(arguments),
            model_construction.of_lines(lines),
            arrangement_w_tcds(),
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

            arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

            with self.subTest(case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_construction.of_lines([]),
                    arrangement_w_tcds(
                        symbols=line_matcher_symbol_context.symbol_table
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=line_matcher_symbol_context.references_assertion
                        ),
                        ExecutionExpectation(
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
