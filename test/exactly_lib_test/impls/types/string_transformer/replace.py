import unittest
from typing import List, Callable, Sequence

from exactly_lib.impls.types.string_transformer import parse_string_transformer as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, prim_asrt__constant
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.regex.test_resources import assertions as asrt_regex
from exactly_lib_test.impls.types.regex.test_resources.assertions import is_reference_to_valid_regex_string_part
from exactly_lib_test.impls.types.regex.test_resources.validation_cases import failing_regex_validation_cases
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax as arg, \
    integration_check, freeze_check
from exactly_lib_test.impls.types.string_transformer.test_resources import may_dep_on_ext_resources
from exactly_lib_test.impls.types.string_transformer.test_resources.integration_check import StExpectation
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import NEA, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources.string_transformer_assertions import \
    is_identity_transformer
from exactly_lib_test.util.test_resources import quoting
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestApplication),
        ReferencedSymbolsShouldBeReportedAndUsed(),
        ValidationShouldFailWhenRegexIsInvalid(),
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [
            arg.syntax_for_replace_transformer('regex', 'replacement', False),
            arg.syntax_for_replace_transformer('regex', 'replacement', True),
        ]


class TransformationCase:
    def __init__(self,
                 name: str,
                 regex: str,
                 replacement: str):
        self.name = name
        self.regex = regex
        self.replacement = replacement


class TestInvalidSyntax(unittest.TestCase):
    def test_failing_parse(self):
        for preserve_new_lines in [False, True]:
            cases = [
                NameAndValue(
                    'no arguments',
                    arg.syntax_for_replace_transformer__custom(Arguments.empty(),
                                                               preserve_new_lines=preserve_new_lines),
                ),
                NameAndValue(
                    'single REGEX argument (missing REPLACEMENT)',
                    arg.syntax_for_replace_transformer__custom(Arguments('regex'),
                                                               preserve_new_lines=preserve_new_lines),
                ),
                NameAndValue(
                    'single REGEX argument (missing REPLACEMENT), but it appears on the following line',
                    arg.syntax_for_replace_transformer__custom(Arguments('regex',
                                                                         ['replacement']),
                                                               preserve_new_lines=preserve_new_lines),
                ),
            ]
            for case in cases:
                with self.subTest(case.name,
                                  preserve_new_lines=preserve_new_lines):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parsers(True).full.parse(case.value.as_remaining_source)


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

        # ACT & ASSERT #
        for preserve_new_lines in [False, True]:
            source = arg.syntax_for_replace_transformer('[E][x][a][c][t][l][y]',
                                                        '"is what I want"',
                                                        preserve_new_lines=preserve_new_lines)
            with self.subTest(preserve_new_lines=preserve_new_lines):
                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_constructor.of_lines(self, input_lines),
                    arrangement_w_tcds(),
                    expectation_of_successful_replace_execution(
                        output_lines=expected_lines
                    )
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
                '\\n',
            ),
        ]
        for preserve_new_lines in [False, True]:
            for case in replacement_string_cases:
                with self.subTest(case.name,
                                  preserve_new_lines=preserve_new_lines):
                    nl_string_symbol = StringConstantSymbolContext(
                        'NL',
                        case.value,
                        default_restrictions=asrt_regex.is_regex_reference_restrictions(),
                    )
                    source = arg.syntax_for_replace_transformer('P',
                                                                nl_string_symbol.name__sym_ref_syntax,
                                                                preserve_new_lines=preserve_new_lines)

                    # ACT & ASSERT #

                    integration_check.CHECKER__PARSE_SIMPLE.check(
                        self,
                        remaining_source(source),
                        model_constructor.of_lines(self, input_lines),
                        arrangement_w_tcds(
                            symbols=nl_string_symbol.symbol_table
                        ),
                        expectation_of_successful_replace_execution(
                            output_lines=expected_lines,
                            symbol_references=nl_string_symbol.references_assertion
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
        for case in cases:
            with self.subTest(case.name):
                nl_string_symbol = StringConstantSymbolContext(
                    'NL',
                    '\n',
                    default_restrictions=asrt_regex.is_regex_reference_restrictions(),
                )
                source = arg.syntax_for_replace_transformer(nl_string_symbol.name__sym_ref_syntax,
                                                            surrounded_by_hard_quotes_str(''),
                                                            )

                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    remaining_source(source),
                    model_constructor.of_lines(self, case.input_value),
                    arrangement_w_tcds(
                        symbols=nl_string_symbol.symbol_table
                    ),
                    expectation_of_successful_replace_execution(
                        output_lines=case.expected_value,
                        symbol_references=nl_string_symbol.references_assertion
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
        for case in cases:
            with self.subTest(case.name):
                nl_string_symbol = StringConstantSymbolContext(
                    'NL',
                    '\n',
                    default_restrictions=asrt_regex.is_regex_reference_restrictions(),
                )
                source = arg.syntax_for_replace_transformer(nl_string_symbol.name__sym_ref_syntax,
                                                            surrounded_by_hard_quotes_str(''),
                                                            preserve_new_lines=True,
                                                            )

                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    remaining_source(source),
                    model_constructor.of_lines(self, case.value),
                    arrangement_w_tcds(
                        symbols=nl_string_symbol.symbol_table
                    ),
                    expectation_of_successful_replace_execution(
                        output_lines=case.value,
                        symbol_references=nl_string_symbol.references_assertion
                    )
                )

    def _check_lines(self,
                     lines_for: Callable[[str], List[str]],
                     source_cases: List[NEA[str, str]]):
        for source_case in source_cases:
            source = arg.syntax_for_replace_transformer(source_case.actual,
                                                        source_case.expected)
            with self.subTest(source_case.name):
                # ACT & ASSERT #

                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_constructor.of_lines(self, lines_for(source_case.actual)),
                    arrangement_w_tcds(),
                    expectation_of_successful_replace_execution(
                        output_lines=lines_for(source_case.expected)
                    )
                )

    def _check_lines_for_constant_regex(self,
                                        lines_for: Callable[[str], List[str]],
                                        source_cases: List[TransformationCase]):
        for source_case in source_cases:
            source = arg.syntax_for_replace_transformer(source_case.regex,
                                                        source_case.replacement)
            with self.subTest(source_case.name):
                # ACT & ASSERT #

                integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                    self,
                    Arguments(source),
                    model_constructor.of_lines(self, lines_for(source_case.regex)),
                    arrangement_w_tcds(),
                    Expectation(
                        ParseExpectation(
                            symbol_references=asrt.is_empty_sequence,
                        ),
                        ExecutionExpectation(
                            main_result=asrt_string_source.pre_post_freeze__matches_lines__identical(
                                asrt.equals(lines_for(source_case.replacement)),
                                may_depend_on_external_resources=asrt.equals(False),
                            )
                        ),
                        adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
                    )
                )

    def _check_lines_for_constant_regex__equivalent_for_preserve_new_lines(self,
                                                                           lines_for: Callable[[str], List[str]],
                                                                           source_cases: List[TransformationCase]):
        for preserve_new_lines in [False, True]:
            for source_case in source_cases:
                source = arg.syntax_for_replace_transformer(source_case.regex,
                                                            source_case.replacement,
                                                            preserve_new_lines=preserve_new_lines)
                with self.subTest(source_case.name,
                                  preserve_new_lines=preserve_new_lines):
                    # ACT & ASSERT #

                    integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                        self,
                        Arguments(source),
                        model_constructor.of_lines(self, lines_for(source_case.regex)),
                        arrangement_w_tcds(),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.is_empty_sequence,
                            ),
                            ExecutionExpectation(
                                main_result=asrt_string_source.pre_post_freeze__matches_lines__identical(
                                    asrt.equals(lines_for(source_case.replacement)),
                                    may_depend_on_external_resources=asrt.equals(False),
                                )
                            ),
                            adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
                        )
                    )


class ReferencedSymbolsShouldBeReportedAndUsed(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        symbol_in_regex = StringConstantSymbolContext('symbol_in_regex',
                                                      'plain string pattern')
        symbol_in_replacement = StringConstantSymbolContext('symbol_in_replacement',
                                                            'the replacement')

        input_lines = [
            symbol_in_regex.str_value,
        ]
        expected_lines = [
            symbol_in_replacement.str_value,
        ]
        quoting_cases = [
            NameAndValue('unquoted', lambda x: x),
            NameAndValue('soft quoted', quoting.surrounded_by_soft_quotes_str),
        ]
        for preserve_new_lines in [False, True]:
            for quoting_case in quoting_cases:
                source = arg.syntax_for_replace_transformer(
                    quoting_case.value(symbol_reference_syntax_for_name(symbol_in_regex.name)),
                    symbol_reference_syntax_for_name(symbol_in_replacement.name),
                    preserve_new_lines=preserve_new_lines,
                )

                with self.subTest(quoting_case.name,
                                  preserve_new_lines=preserve_new_lines):
                    # ACT & ASSERT #

                    integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                        self,
                        Arguments(source),
                        model_constructor.of_lines(self, input_lines),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts([
                                symbol_in_regex,
                                symbol_in_replacement,
                            ]),
                        ),
                        expectation_of_successful_replace_execution(
                            symbol_references=
                            asrt.matches_sequence([
                                is_reference_to_valid_regex_string_part(symbol_in_regex.name),
                                symbol_in_replacement.reference_assertion__any_data_type,
                            ]),
                            output_lines=expected_lines,
                        )
                    )


class ValidationShouldFailWhenRegexIsInvalid(unittest.TestCase):
    def runTest(self):
        for preserve_new_lines in [False, True]:
            for regex_case in failing_regex_validation_cases():
                source = arg.syntax_for_replace_transformer(regex_case.regex_string,
                                                            'arbitrary_replacement',
                                                            preserve_new_lines=preserve_new_lines)
                with self.subTest(regex_case.case_name,
                                  preserve_new_lines=preserve_new_lines):
                    integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
                        self,
                        Arguments(source),
                        model_constructor.arbitrary(self),
                        arrangement_w_tcds(
                            symbols=regex_case.symbol_table
                        ),
                        Expectation(
                            ParseExpectation(
                                symbol_references=asrt.matches_sequence(regex_case.reference_assertions),
                            ),
                            ExecutionExpectation(
                                validation=regex_case.expectation
                            ),
                            prim_asrt__constant(
                                is_identity_transformer(False)
                            ),
                        )
                    )


def expectation_of_successful_replace_execution(
        output_lines: List[str],
        symbol_references: Assertion[Sequence[SymbolReference]] = asrt.anything_goes(),
) -> StExpectation:
    return integration_check.expectation_of_successful_execution_2(
        output_lines,
        False,
        symbol_references,
        False,
        adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
    )
