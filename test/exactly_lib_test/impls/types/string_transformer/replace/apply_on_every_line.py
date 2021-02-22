import unittest
from typing import List, Callable, Sequence, Optional

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ExecutionExpectation, \
    prim_asrt__constant, MultiSourceExpectation
from exactly_lib_test.impls.types.regex.test_resources import assertions as asrt_regex
from exactly_lib_test.impls.types.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.replace.test_resources import \
    expectation_of_successful_replace_execution, expectation_of_successful_replace_execution__multi
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check, freeze_check
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import ReplaceRegexAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.data import data_restrictions_assertions as asrt_ref_rest
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import LineMatcherAbsStx, \
    LineMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.line_matcher import LineMatcherSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer
from exactly_lib_test.util.test_resources import quoting


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestApplication),
        ReferencedSymbolsShouldBeReportedAndUsed(),
        ValidationShouldFailWhenRegexIsInvalid(),
    ])


class TransformationCase:
    def __init__(self,
                 name: str,
                 regex: str,
                 replacement: str):
        self.name = name
        self.regex = regex
        self.replacement = replacement


class LineFilterCase:
    def __init__(self,
                 syntax: Optional[LineMatcherAbsStx],
                 symbols: Sequence[SymbolContext],
                 ):
        self._syntax = syntax
        self._symbols = symbols

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._syntax is not None

    @property
    def syntax(self) -> Optional[LineMatcherAbsStx]:
        return self._syntax

    @property
    def symbols(self) -> List[SymbolContext]:
        return list(self._symbols)

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self._symbols)

    @property
    def references_assertion(self) -> Assertion[Sequence[SymbolReference]]:
        return SymbolContext.references_assertion_of_contexts(self._symbols)

    def references_assertion__followed_by(self,
                                          reference_assertions: List[Assertion[SymbolReference]]
                                          ) -> Assertion[Sequence[SymbolReference]]:
        ret_val = [
            symbol.reference_assertion
            for symbol in self._symbols
        ]
        ret_val += reference_assertions
        return asrt.matches_sequence(ret_val)


LINE_FILTER_CASES: Sequence[NameAndValue[LineFilterCase]] = (
    NameAndValue(
        'wo filer',
        LineFilterCase(None, ()),
    ),
    NameAndValue(
        'w filer',
        LineFilterCase(
            LineMatcherSymbolReferenceAbsStx('LINE_MATCHER'),
            (LineMatcherSymbolContext.of_primitive_constant('LINE_MATCHER', True),)
        ),
    ),
)


class TestApplication(unittest.TestCase):
    def test_every_line_SHOULD_be_transformed(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return with_appended_new_lines([
                'unidentified flying {}'.format(pattern_matching_string),
                '{} oriented'.format(pattern_matching_string),
                'I {}!'.format(pattern_matching_string),
            ])

        source_cases = [
            TransformationCase('single word tokens',
                               'transformer',
                               'object',
                               ),
            TransformationCase('multi word tokens',
                               quoting.surrounded_by_soft_quotes_str('t r a n s f o r m er'),
                               quoting.surrounded_by_soft_quotes_str('o b j e c t'),
                               ),
        ]
        # ACT & ASSERT #
        self._check_lines_for_constant_regex__equivalent_for_preserve_new_lines(lines, source_cases)

    def test_every_match_on_a_line_SHOULD_be_replaced(self):
        # ARRANGE #
        def lines(pattern_matching_string: str) -> List[str]:
            return [
                'we are {0} and they are {0} too'.format(pattern_matching_string),
            ]

        source_cases = [
            TransformationCase('single word tokens',
                               'here',
                               'there',
                               ),
            TransformationCase('multi word tokens',
                               quoting.surrounded_by_soft_quotes_str('h e r e'),
                               quoting.surrounded_by_soft_quotes_str('t h e r e'),
                               ),
        ]
        # ACT & ASSERT #
        self._check_lines_for_constant_regex__equivalent_for_preserve_new_lines(lines, source_cases)

    def test_regular_expression_SHOULD_be_matched(self):
        # ARRANGE #
        input_lines = [
            'Exactly',
        ]
        expected_lines = [
            'is what I want',
        ]

        for line_filter_case in LINE_FILTER_CASES:
            for preserve_new_lines in [False, True]:
                source = ReplaceRegexAbsStx.of_str('[E][x][a][c][t][l][y]',
                                                   quoting.surrounded_by_str('is what I want',
                                                                             QuoteType.HARD),
                                                   preserve_new_lines=preserve_new_lines,
                                                   lines_filter=line_filter_case.value.syntax,
                                                   )
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                    self,
                    source,
                    model_constructor.of_lines(self, input_lines),
                    arrangement_w_tcds(
                        symbols=line_filter_case.value.symbol_table,
                    ),
                    expectation_of_successful_replace_execution__multi(
                        symbol_references=line_filter_case.value.references_assertion,
                        may_depend_on_external_resources=line_filter_case.value.may_depend_on_external_resources,
                        output_lines=expected_lines,
                    ),
                    sub_test_identifiers={
                        'preserve_new_lines': preserve_new_lines,
                    }
                )

    def test_insertion_of_new_line_into_a_line_SHOULD_split_that_line(self):
        # ARRANGE #
        input_lines = [
            'P\n',
            '---\n',
            'aPbPc\n',
            '---\n',
            'P',
        ]
        expected_lines = [
            '\n',
            '\n',
            '---\n',
            'a\n',
            'b\n',
            'c\n',
            '---\n',
            '\n',
        ]
        replacement_string_cases = [
            NameAndValue(
                'literate new line',
                '\n',
            ),
            NameAndValue(
                'new line escape sequence, as interpreted by Python replace',
                r'\n',
            ),
        ]
        for line_filter_case in LINE_FILTER_CASES:
            for preserve_new_lines in [False, True]:
                for case in replacement_string_cases:
                    with self.subTest(case.name,
                                      preserve_new_lines=preserve_new_lines,
                                      line_filtering=line_filter_case.name):
                        nl_string_symbol = StringConstantSymbolContext(
                            'NL',
                            case.value,
                            default_restrictions=asrt_regex.is_reference_restrictions__regex(),
                        )
                        all_symbols = line_filter_case.value.symbols + [nl_string_symbol]
                        source = ReplaceRegexAbsStx(StringLiteralAbsStx('P'),
                                                    nl_string_symbol.abstract_syntax,
                                                    preserve_new_lines=preserve_new_lines,
                                                    lines_filter=line_filter_case.value.syntax,
                                                    )

                        # ACT & ASSERT #

                        integration_check.CHECKER__PARSE_SIMPLE.check__abs_stx(
                            self,
                            source,
                            model_constructor.of_lines(self, input_lines),
                            arrangement_w_tcds(
                                symbols=SymbolContext.symbol_table_of_contexts(all_symbols)
                            ),
                            expectation_of_successful_replace_execution(
                                symbol_references=SymbolContext.references_assertion_of_contexts(all_symbols),
                                may_depend_on_external_resources=line_filter_case.value.may_depend_on_external_resources,
                                output_lines=expected_lines,
                            )
                        )

    def test_removal_of_new_lines_SHOULD_join_lines(self):
        # ARRANGE #
        cases = [
            NIE('final line not ended by new-line',
                input_value=[
                    '1\n',
                    '2\n',
                    '3',
                ],
                expected_value=[
                    '123',
                ]
                ),
            NIE('final line ended by new-line',
                input_value=[
                    '1\n',
                    '2\n',
                    '3\n',
                ],
                expected_value=[
                    '123',
                ]
                ),
        ]
        for line_filter_case in LINE_FILTER_CASES:
            for case in cases:
                with self.subTest(model=case.name,
                                  line_filtering=line_filter_case.name):
                    nl_string_symbol = StringConstantSymbolContext(
                        'NL',
                        '\n',
                        default_restrictions=asrt_regex.is_reference_restrictions__regex(),
                    )
                    all_symbols = line_filter_case.value.symbols + [nl_string_symbol]
                    source = ReplaceRegexAbsStx(nl_string_symbol.abstract_syntax,
                                                StringLiteralAbsStx.empty_string(),
                                                preserve_new_lines=False,
                                                lines_filter=line_filter_case.value.syntax,
                                                )

                    # ACT & ASSERT #
                    integration_check.CHECKER__PARSE_SIMPLE.check__abs_stx(
                        self,
                        source,
                        model_constructor.of_lines(self, case.input_value),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                        ),
                        expectation_of_successful_replace_execution(
                            symbol_references=SymbolContext.references_assertion_of_contexts(all_symbols),
                            may_depend_on_external_resources=line_filter_case.value.may_depend_on_external_resources,
                            output_lines=case.expected_value,
                        )
                    )

    def test_new_lines_may_not_be_removed_when_new_lines_are_preserved(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'final line not ended by new-line',
                [
                    '1\n',
                    '2\n',
                    '3',
                ],
            ),
            NameAndValue(
                'final line ended by new-line',
                [
                    '1\n',
                    '2\n',
                    '3\n',
                ],
            ),
        ]
        for line_filter_case in LINE_FILTER_CASES:
            for case in cases:
                with self.subTest(model=case.name,
                                  line_filtering=line_filter_case.name):
                    nl_string_symbol = StringConstantSymbolContext(
                        'NL',
                        '\n',
                        default_restrictions=asrt_regex.is_reference_restrictions__regex(),
                    )
                    all_symbols = line_filter_case.value.symbols + [nl_string_symbol]
                    source = ReplaceRegexAbsStx(nl_string_symbol.abstract_syntax,
                                                StringLiteralAbsStx.empty_string(),
                                                preserve_new_lines=True,
                                                lines_filter=line_filter_case.value.syntax,
                                                )

                    # ACT & ASSERT #
                    integration_check.CHECKER__PARSE_SIMPLE.check__abs_stx(
                        self,
                        source,
                        model_constructor.of_lines(self, case.value),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                        ),
                        expectation_of_successful_replace_execution(
                            symbol_references=SymbolContext.references_assertion_of_contexts(all_symbols),
                            may_depend_on_external_resources=line_filter_case.value.may_depend_on_external_resources,
                            output_lines=case.value,
                        )
                    )

    def _check_lines_for_constant_regex__equivalent_for_preserve_new_lines(self,
                                                                           lines_for: Callable[[str], List[str]],
                                                                           source_cases: List[TransformationCase],
                                                                           ):
        for line_filter_case in LINE_FILTER_CASES:
            for preserve_new_lines in [False, True]:
                for source_case in source_cases:
                    source = ReplaceRegexAbsStx.of_str(source_case.regex,
                                                       source_case.replacement,
                                                       preserve_new_lines=preserve_new_lines,
                                                       lines_filter=line_filter_case.value.syntax,
                                                       )
                    # ACT & ASSERT #
                    integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                        self,
                        source,
                        model_constructor.of_lines(self, lines_for(source_case.regex)),
                        arrangement_w_tcds(
                            symbols=line_filter_case.value.symbol_table,
                        ),
                        MultiSourceExpectation(
                            symbol_references=line_filter_case.value.references_assertion,
                            execution=ExecutionExpectation(
                                main_result=asrt_string_source.pre_post_freeze__matches_lines__identical(
                                    asrt.equals(lines_for(source_case.replacement)),
                                    may_depend_on_external_resources=asrt.equals(
                                        line_filter_case.value.may_depend_on_external_resources
                                    ),
                                )
                            ),
                            adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
                        ),
                        sub_test_identifiers={
                            'preserve_new_lines': preserve_new_lines,
                            'source': repr(source.as_str__default()),
                            'line_filter_case': line_filter_case.name,
                        }
                    )


class ReferencedSymbolsShouldBeReportedAndUsed(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        symbol_in_regex = StringConstantSymbolContext(
            'symbol_in_regex',
            'plain string pattern',
            default_restrictions=asrt_regex.is_reference_restrictions__regex()
        )
        symbol_in_replacement = StringConstantSymbolContext(
            'symbol_in_replacement',
            'the replacement',
            default_restrictions=asrt_ref_rest.is_reference_restrictions__convertible_to_string(),
        )

        input_lines = [
            symbol_in_regex.str_value,
        ]
        expected_lines = [
            symbol_in_replacement.str_value,
        ]
        quoting_cases = [
            None,
            QuoteType.SOFT,
        ]
        for line_filter_case in LINE_FILTER_CASES:
            all_symbols = line_filter_case.value.symbols + [
                symbol_in_regex,
                symbol_in_replacement,
            ]
            for preserve_new_lines in [False, True]:
                for quoting_variant in quoting_cases:
                    source = ReplaceRegexAbsStx(
                        StringLiteralAbsStx(symbol_in_regex.name__sym_ref_syntax, quoting_variant),
                        symbol_in_replacement.abstract_syntax,
                        preserve_new_lines=preserve_new_lines,
                        lines_filter=line_filter_case.value.syntax,
                    )
                    # ACT & ASSERT #

                    integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                        self,
                        source,
                        model_constructor.of_lines(self, input_lines),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                        ),
                        expectation_of_successful_replace_execution__multi(
                            symbol_references=
                            SymbolContext.references_assertion_of_contexts(all_symbols),
                            may_depend_on_external_resources=line_filter_case.value.may_depend_on_external_resources,
                            output_lines=expected_lines,
                        ),
                        sub_test_identifiers={
                            'preserve_new_lines': preserve_new_lines,
                            'quoting': quoting_variant,
                            'line_filtering': line_filter_case.name,
                        }
                    )


class ValidationShouldFailWhenRegexIsInvalid(unittest.TestCase):
    def runTest(self):
        for line_filter_case in LINE_FILTER_CASES:
            for preserve_new_lines in [False, True]:
                for regex_case in failing_regex_validation_cases():
                    all_symbols = line_filter_case.value.symbols + regex_case.symbols
                    source = ReplaceRegexAbsStx.of_str(regex_case.regex_string,
                                                       'arbitrary_replacement',
                                                       preserve_new_lines=preserve_new_lines,
                                                       lines_filter=line_filter_case.value.syntax,
                                                       )
                    # ACT & ASSERT #
                    integration_check.CHECKER__PARSE_FULL.check__abs_stx__layout__std_source_variants(
                        self,
                        source,
                        model_constructor.arbitrary(self),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(all_symbols)
                        ),
                        MultiSourceExpectation(
                            symbol_references=line_filter_case.value.references_assertion__followed_by(
                                regex_case.reference_assertions
                            ),
                            execution=ExecutionExpectation(
                                validation=regex_case.expectation
                            ),
                            primitive=prim_asrt__constant(
                                is_identity_transformer(False)
                            ),
                        ),
                        sub_test_identifiers={
                            'regex_case': regex_case.case_name,
                            'preserve_new_lines': preserve_new_lines,
                            'lines_filtering': line_filter_case.name,
                        }
                    )
