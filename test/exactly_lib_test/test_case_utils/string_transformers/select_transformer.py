import unittest

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver, LineMatcherReferenceResolver
from exactly_lib.test_case_utils.string_transformer import transformers as sut
from exactly_lib.test_case_utils.string_transformer.resolvers import StringTransformerSelectResolver
from exactly_lib.test_case_utils.string_transformer.transformers import SelectStringTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherResolverConstantTestImpl, \
    is_line_matcher_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.line_matcher.test_resources import arguments_building as lm_arg
from exactly_lib_test.test_case_utils.line_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as st_args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.string_transformers.test_resources import resolver_assertions as asrt_resolver
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import LineMatcherFromPredicates, is_identical_to


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSelectTransformer),
        unittest.makeSuite(TestSelectTransformerResolver),
        ValidatorShouldValidateLineMatcher(),
    ])


class TestSelectTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.SelectStringTransformer(sub_string_line_matcher('MATCH'))
        self.assertFalse(transformer.is_identity_transformer)

    def test_select_with_sub_string_matcher(self):
        transformer = sut.SelectStringTransformer(sub_string_line_matcher('MATCH'))
        cases = [
            NameAndValue('no lines',
                         ([],
                          [])
                         ),
            NameAndValue('single line that matches',
                         (['MATCH'],
                          ['MATCH'])
                         ),
            NameAndValue('single line that does not match',
                         (['not a match'],
                          [])
                         ),
            NameAndValue('some lines matches',
                         ([
                              'first line is a MATCH',
                              'second line is not a match',
                              'third line MATCH:es',
                              'fourth line not',
                          ],
                          [
                              'first line is a MATCH',
                              'third line MATCH:es',
                          ])
                         ),
        ]
        for case in cases:
            input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                # ACT #
                actual = transformer.transform(iter(input_lines))
                # ASSERT #
                actual_lines = list(actual)
                self.assertEqual(expected_output_lines,
                                 actual_lines)

    def test_other_scenarios(self):
        cases = [
            NameAndValue(
                'trailing new lines should be removed from line matcher model, but not from transformer output',
                (LineMatcherFromPredicates(line_contents_predicate=lambda x: x == 'X'),
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
                (LineMatcherFromPredicates(line_num_predicate=lambda x: x in {1, 3}),
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
        for case in cases:
            line_matcher, input_lines, expected_output_lines = case.value
            with self.subTest(case_name=case.name):
                transformer = sut.SelectStringTransformer(line_matcher)
                # ACT #
                actual = transformer.transform(iter(input_lines))
                # ASSERT #
                actual_lines = list(actual)
                self.assertEqual(expected_output_lines,
                                 actual_lines)


class TestSelectTransformerResolver(unittest.TestCase):
    def test_sans_references(self):
        line_matcher = LineMatcherConstant(False)

        resolved_value = SelectStringTransformer(line_matcher)
        assertion_on_resolver = asrt_resolver.resolved_value_equals_string_transformer(
            resolved_value,
            references=asrt.is_empty_sequence)

        actual_resolver = StringTransformerSelectResolver(
            LineMatcherResolverConstantTestImpl(line_matcher))
        assertion_on_resolver.apply_without_message(self,
                                                    actual_resolver)

    def test_references(self):
        # ARRANGE #
        symbol = NameAndValue('matcher_symbol',
                              LineMatcherConstant(True))

        actual_resolver = StringTransformerSelectResolver(
            LineMatcherReferenceResolver(symbol.name))

        # EXPECTATION #

        expected_resolved_value = SelectStringTransformer(symbol.value)

        assertion_on_resolver = asrt_resolver.resolved_value_equals_string_transformer(
            expected_resolved_value,
            references=asrt.matches_sequence(([
                is_line_matcher_reference_to(symbol.name)
            ])),
            symbols=SymbolTable({
                symbol.name: container(LineMatcherConstantResolver(symbol.value)),
            }))
        # ACT & ASSERT #
        assertion_on_resolver.apply_without_message(self,
                                                    actual_resolver)


class ValidatorShouldValidateLineMatcher(unittest.TestCase):
    def runTest(self):
        for case in validation_cases.failing_validation_cases():
            line_matcher_symbol_context = case.value.symbol_context
            line_matcher_arg = lm_arg.SymbolReference(line_matcher_symbol_context.name)

            arguments = st_args.syntax_for_select_transformer(str(line_matcher_arg))

            with self.subTest(case.name):
                integration_check.check(
                    self,
                    remaining_source(arguments),
                    [],
                    integration_check.Arrangement(
                        symbols=line_matcher_symbol_context.symbol_table
                    ),
                    integration_check.Expectation(
                        validation=case.value.expectation,
                        symbol_references=line_matcher_symbol_context.references_assertion
                    )
                )


def sub_string_line_matcher(sub_string: str) -> LineMatcher:
    return LineMatcherFromPredicates(line_contents_predicate=lambda actual: sub_string in actual)
