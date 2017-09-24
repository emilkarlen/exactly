import unittest

from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver, LineMatcherReferenceResolver
from exactly_lib.test_case_utils.lines_transformer import transformers as sut
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerSelectResolver
from exactly_lib.test_case_utils.lines_transformer.transformers import SelectLinesTransformer
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherResolverConstantTestImpl, \
    is_line_matcher_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_case_utils.lines_transformers.test_resources import resolver_assertions as asrt_resolver
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSelectTransformer),
        unittest.makeSuite(TestSelectTransformerResolver),
    ])


class TestSelectTransformer(unittest.TestCase):
    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.SelectLinesTransformer(SubStringLineMatcher('MATCH'))
        self.assertFalse(transformer.is_identity_transformer)

    def test_select(self):
        home_and_sds = fake_home_and_sds()

        transformer = sut.SelectLinesTransformer(SubStringLineMatcher('MATCH'))
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
                actual = transformer.transform(home_and_sds, iter(input_lines))
                # ASSERT #
                actual_lines = list(actual)
                self.assertEqual(expected_output_lines,
                                 actual_lines)


class TestSelectTransformerResolver(unittest.TestCase):
    def test_sans_references(self):
        line_matcher = LineMatcherConstant(False)

        resolved_value = SelectLinesTransformer(line_matcher)
        assertion_on_resolver = asrt_resolver.resolved_value_equals_lines_transformer(
            resolved_value,
            references=asrt.is_empty_list)

        actual_resolver = LinesTransformerSelectResolver(
            LineMatcherResolverConstantTestImpl(line_matcher))
        assertion_on_resolver.apply_without_message(self,
                                                    actual_resolver)

    def test_references(self):
        # ARRANGE #
        symbol = NameAndValue('matcher_symbol',
                              LineMatcherConstant(True))

        actual_resolver = LinesTransformerSelectResolver(
            LineMatcherReferenceResolver(symbol.name))

        # EXPECTATION #

        expected_resolved_value = SelectLinesTransformer(symbol.value)

        assertion_on_resolver = asrt_resolver.resolved_value_equals_lines_transformer(
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


class SubStringLineMatcher(LineMatcher):
    def __init__(self, sub_string: str):
        self.sub_string = sub_string

    def matches(self, line: str) -> bool:
        return self.sub_string in line
