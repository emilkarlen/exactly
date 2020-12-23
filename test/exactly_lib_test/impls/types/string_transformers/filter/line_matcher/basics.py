import unittest
from typing import List, Sequence

from exactly_lib.impls.types.string_transformer import parse_string_transformer as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.impls.types.line_matcher.test_resources import arguments_building as lm_args
from exactly_lib_test.impls.types.line_matcher.test_resources import models as line_matcher_models
from exactly_lib_test.impls.types.line_matcher.test_resources import validation_cases
from exactly_lib_test.impls.types.line_matcher.test_resources.line_matchers import LineMatcherThatCollectsModels
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, Expectation, \
    ParseExpectation, ExecutionExpectation, arrangement_wo_tcds, prim_asrt__any
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax as st_args
from exactly_lib_test.impls.types.string_transformers.test_resources import freeze_check
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources.integration_check import \
    expectation_of_successful_execution, StExpectation
from exactly_lib_test.section_document.test_resources import parse_source
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources import symbol_syntax
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.test_resources import line_matcher
from exactly_lib_test.type_val_deps.types.test_resources.line_matcher import LineMatcherSymbolContext, \
    LineMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.test_resources.primitives import is_identical_to, \
    line_matcher_from_predicates


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
        unittest.makeSuite(TestFiltering),
        _TestLineMatcherModelsGivenToLineMatcher(),
        unittest.makeSuite(TestLineMatcherPrimitive),
        ValidatorShouldValidateLineMatcher(),
        TestMayDependOnExternalResourcesShouldBeFalseRegardlessOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeFalseRegardlessOfSourceModel(unittest.TestCase):
    # ... since the applied LineMatcher may have external dependencies (e.g. "run")

    def runTest(self):
        # ARRANGE #

        matcher = LineMatcherSymbolContext.of_primitive_constant(
            'line_matcher_symbol',
            False,
        )
        line_matcher_arg = lm_args.SymbolReference(matcher.name)

        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

        # ACT & ASSERT #
        for may_depend_on_external_resources in [False, True]:
            with self.subTest(may_depend_on_external_resources=may_depend_on_external_resources):
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    remaining_source(arguments),
                    model_constructor.empty(self,
                                            may_depend_on_external_resources=may_depend_on_external_resources),
                    arrangement_w_tcds(
                        symbols=matcher.symbol_table
                    ),
                    expectation_of_successful_filter_execution(
                        symbol_references=asrt.matches_singleton_sequence(
                            matcher.reference_assertion
                        ),
                        output_lines=[],
                    )
                )


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
            input_=model_constructor.of_lines(self, model),
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
                may_depend_on_external_resources=True,
                frozen_may_depend_on_external_resources=asrt.anything_goes(),
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
        line_matcher_arg = lm_args.SymbolReference(matcher.name)

        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            Arguments(arguments),
            model_constructor.of_lines(self, []),
            arrangement_w_tcds(
                symbols=matcher.symbol_table
            ),
            expectation_of_successful_filter_execution(
                symbol_references=asrt.matches_singleton_sequence(
                    matcher.reference_assertion
                ),
                output_lines=[],
            )
        )

    def test_every_line_SHOULD_be_filtered(self):
        matcher = LineMatcherSymbolContext.of_primitive(
            'line_matcher_symbol',
            sub_string_line_matcher('MATCH'),
        )
        line_matcher_arg = lm_args.SymbolReference(matcher.name)
        cases = [
            NEA('no lines',
                [],
                [],
                ),
            NEA('single line that matches',
                ['a MATCH'],
                ['a MATCH'],
                ),
            NEA('single line that matches, ended by new-line',
                ['a MATCH\n'],
                ['a MATCH\n'],
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
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_constructor.of_lines(self, case.actual),
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
        line_matcher_arg = lm_args.SymbolReference(line_matcher_name)
        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

        for case in cases:
            matcher, input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                # ACT & ASSERT #

                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_constructor.of_lines(self, input_lines),
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


class _TestLineMatcherModelsGivenToLineMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        input_lines = [
            '1st',
            '2nd',
            '3rd',
        ]
        expected_line_matcher_models = line_matcher_models.models_for_lines__validated(input_lines)
        string_transformer_model = model_constructor.of_lines_wo_nl(self, input_lines)

        models_output = []
        line_matcher = LineMatcherSymbolContext.of_primitive(
            'MATCHER',
            LineMatcherThatCollectsModels(models_output, True),
        )

        line_matcher_arg = lm_args.SymbolReference(line_matcher.name)
        arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=remaining_source(arguments),
            input_=string_transformer_model,
            arrangement=arrangement_w_tcds(
                symbols=line_matcher.symbol_table,
            ),
            expectation=Expectation(
                ParseExpectation(
                    symbol_references=line_matcher.references_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt.anything_goes(),
                ),
                prim_asrt__any
            ),
        )
        self.assertEqual(expected_line_matcher_models,
                         models_output,
                         'models given to line matcher')


class TestLineMatcherPrimitive(unittest.TestCase):
    def test(self):
        # ARRANGE #

        reg_ex_pattern = 'const_pattern'
        arguments = st_args.syntax_for_filter_transformer(str(
            lm_args.Contents(sm_args.Matches(reg_ex_pattern)))
        )

        lines = [
            reg_ex_pattern + '\n',
            'non matching line',
        ]
        expected_lines = [
            reg_ex_pattern + '\n',
        ]

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            Arguments(arguments),
            model_constructor.of_lines(self, lines),
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
            line_matcher_arg = lm_args.SymbolReference(line_matcher_symbol_context.name)

            arguments = st_args.syntax_for_filter_transformer(str(line_matcher_arg))

            with self.subTest(case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
                    self,
                    Arguments(arguments),
                    model_constructor.of_lines(self, []),
                    arrangement_wo_tcds(
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
        True,
        asrt.anything_goes(),
        symbol_references,
        False,
        adv=freeze_check.single_access_of_source_model_after_freeze__that_is_not_freeze,
    )
