import unittest
from typing import List, Tuple, Iterator, TypeVar, Callable, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util import collection
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.source import layout as tokens_layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.test_utils import NEA, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SourceCase(tuple):
    def __new__(cls,
                source: ParseSource,
                expectation: ValueAssertion[ParseSource],
                ):
        return tuple.__new__(cls, (source,
                                   expectation))

    @property
    def source(self) -> ParseSource:
        return self[0]

    @property
    def expectation(self) -> ValueAssertion[ParseSource]:
        return self[1]


class NSourceCase(tuple):
    def __new__(cls,
                name: str,
                source: ParseSource,
                expectation: ValueAssertion[ParseSource],
                ):
        return tuple.__new__(cls, (name, source, expectation))

    @property
    def name(self) -> str:
        return self[0]

    @property
    def source(self) -> ParseSource:
        return self[1]

    @property
    def expectation(self) -> ValueAssertion[ParseSource]:
        return self[2]


def equivalent_source_variants__with_source_check__consume_last_line(put: unittest.TestCase,
                                                                     instruction_argument: str,
                                                                     ) -> Iterator[ParseSource]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    instruction_argument = instruction_argument.rstrip('\n')
    num_source_lines = instruction_argument.count('\n') + 1
    for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines):
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants__with_source_check__consume_last_line_2(
        instruction_argument: str,
) -> List[Tuple[SourceCase]]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    num_source_lines = instruction_argument.count('\n') + 1
    return [
        SourceCase(
            remaining_source(instruction_argument, following_lines),
            source_assertion,
        )
        for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines)
    ]


def equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
        syntax: AbstractSyntax,
) -> List[NameAndValue[SourceCase]]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    tokens = syntax.tokenization()

    def cases_for(layout_case: NameAndValue[tokens_layout.LayoutSpec]
                  ) -> List[NameAndValue[SourceCase]]:
        source_str = tokens.layout(layout_case.value)
        num_source_lines = source_str.count('\n') + 1
        return [
            NameAndValue(
                'layout={}, following_lines={}'.format(
                    layout_case.name,
                    repr(following_lines)
                ),
                SourceCase(
                    remaining_source(source_str, following_lines),
                    source_assertion,
                )
            )
            for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines)
        ]

    return collection.concat_list([
        cases_for(layout_case)
        for layout_case in tokens_layout.STANDARD_LAYOUT_SPECS
    ])


def equivalent_source_variants__consume_last_line__s__nsc(
        source: str,
) -> List[NSourceCase]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    num_source_lines = source.count('\n') + 1

    return [
        NSourceCase(
            'following_lines={}'.format(repr(following_lines)),
            _remaining_source__original_plus_extra_lines(source, following_lines),
            source_assertion,
        )
        for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines)
    ]


def equivalent_source_variants__with_source_check__multi_line(put: unittest.TestCase,
                                                              instruction_argument: Arguments,
                                                              ) -> Iterator[ParseSource]:
    """
    Checks that the first line of the source has been consumed.

    Assumes that the body of the loop parses using the given source.
    """
    for following_lines, source_assertion in _source_variant_test_cases__multi_line(instruction_argument.num_lines):
        with put.subTest(following_lines=repr(following_lines)):
            source = instruction_argument.followed_by_lines(following_lines).as_remaining_source
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants_for_consume_until_end_of_last_line(
        arguments: Arguments
) -> List[Tuple[SourceCase]]:
    return [
        SourceCase(
            arguments.followed_by_lines(extra_lines).as_remaining_source,
            assertion,
        )
        for extra_lines, assertion in
        _equivalent_source_variants_for_consume_until_end_of_last_line(arguments.num_lines)
    ]


def equivalent_source_variants_for_consume_until_end_of_last_line2(
        arguments: Arguments
) -> List[NIE[ParseSource, ValueAssertion[ParseSource]]]:
    return [
        NIE(
            repr(extra_lines),
            assertion,
            arguments.followed_by_lines(extra_lines).as_remaining_source,
        )
        for extra_lines, assertion in
        _equivalent_source_variants_for_consume_until_end_of_last_line(arguments.num_lines)
    ]


def equivalent_source_variants_for_consume_until_end_of_last_line_3(
        arguments: str
) -> List[NIE[ParseSource, ValueAssertion[ParseSource]]]:
    return [
        NIE(
            'following_lines={}'.format(repr(extra_lines)),
            assertion,
            _remaining_source__original_plus_extra_lines(arguments, extra_lines),
        )
        for extra_lines, assertion in
        _equivalent_source_variants_for_consume_until_end_of_last_line(arguments.count('\n') + 1)
    ]


SourceStr2SourceVariants = Callable[[str], Sequence[NSourceCase]]


def equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc(
        arguments: str
) -> List[NSourceCase]:
    return [
        NSourceCase(
            'following_lines={}'.format(repr(extra_lines)),
            _remaining_source__original_plus_extra_lines(arguments, extra_lines),
            assertion,
        )
        for extra_lines, assertion in
        _equivalent_source_variants_for_consume_until_end_of_last_line(arguments.count('\n') + 1)
    ]


def equivalent_source_variants__for_expression_parser(
        put: unittest.TestCase,
        original_arguments: Arguments,
) -> Iterator[ParseSource]:
    """
    Assumes that the body of the loop parses using the given source.
    """
    for following_arguments, source_assertion in _source_variants_with__for_expression_parser(
            original_arguments.num_lines):
        with put.subTest(additional_arguments_on_same_line=repr(following_arguments.first_line),
                         additional_lines=repr(following_arguments.following_lines)):
            source = original_arguments.last_line_followed_by(following_arguments,
                                                              first_line_separator='').as_remaining_source
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


T = TypeVar('T')


def equivalent_source_variants__for_expression_parser_2(
        original_arguments: Arguments,
) -> List[NEA[ValueAssertion[ParseSource], ParseSource]]:
    num_lines = original_arguments.num_lines
    return [
        NEA(
            name='additional_arguments_on_same_line={}, additional_lines={}'.format(
                repr(following_arguments.first_line),
                repr(following_arguments.following_lines),
            ),
            expected=source_assertion,
            actual=original_arguments.last_line_followed_by(following_arguments,
                                                            first_line_separator='').as_remaining_source

        )
        for following_arguments, source_assertion in _source_variants_with__for_expression_parser(num_lines)
    ]


def equivalent_source_variants__for_expression_parser_3(
        original_source: str,
) -> List[NEA[ValueAssertion[ParseSource], ParseSource]]:
    return equivalent_source_variants__for_expression_parser_2(
        Arguments.of_preformatted(original_source)
    )


def equivalent_source_variants__for_expression_parser_3__nie(
        original_source: str,
) -> List[NIE[ParseSource, ValueAssertion[ParseSource]]]:
    return [
        NIE(nea.name, nea.expected, nea.actual)
        for nea in equivalent_source_variants__for_expression_parser_3(original_source)
    ]


def equivalent_source_variants__for_expr_parse__s__nsc(original_source: str) -> List[NSourceCase]:
    return [
        NSourceCase(nea.name, nea.actual, nea.expected)
        for nea in equivalent_source_variants__for_expression_parser_3(original_source)
    ]


def equivalent_source_variants__with_source_check__for_full_line_expression_parser(
        original_arguments: Arguments,
) -> List[NEA[ValueAssertion[ParseSource], ParseSource]]:
    num_lines = original_arguments.num_lines
    return [
        NEA(
            name='following_lines={}'.format(
                repr(following_lines),
            ),
            expected=source_assertion,
            actual=original_arguments.followed_by_lines(following_lines).as_remaining_source

        )
        for following_lines, source_assertion in _source_variants_with__for_full_line_expression_parser(num_lines)
    ]


def equivalent_source_variants__for_full_line_expr_parse__s__nsc(
        original_arguments: str,
) -> List[NSourceCase]:
    num_lines = original_arguments.count('\n') + 1
    return [
        NSourceCase(
            'following_lines={}'.format(repr(following_lines)),
            _remaining_source__original_plus_extra_lines(original_arguments, following_lines),
            source_assertion,
        )
        for following_lines, source_assertion in _source_variants_with__for_full_line_expression_parser(num_lines)
    ]


def equivalent_source_variants(put: unittest.TestCase,
                               instruction_argument: str) -> Iterator[ParseSource]:
    for following_lines, source_assertion in _SOURCE_VARIANT_TEST_CASES:
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source


def equivalent_source_variants_with_assertion(put: unittest.TestCase,
                                              instruction_argument: str,
                                              ) -> Iterator[Tuple[ParseSource, ValueAssertion[ParseSource]]]:
    for following_lines, source_assertion in _SOURCE_VARIANT_TEST_CASES:
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source, source_assertion


def _source_variant_test_cases__multi_line(num_source_lines: int
                                           ) -> List[Tuple[List[str], ValueAssertion[ParseSource]]]:
    return [
        ([], asrt_source.source_is_at_end),
        (['following line'], asrt_source.is_at_beginning_of_line(num_source_lines + 1)),
        (['  '], asrt_source.is_at_beginning_of_line(num_source_lines + 1)),
    ]


def _source_variants_with_accepted_following_content_on_same_line(
        num_source_lines: int
) -> List[Tuple[Arguments, ValueAssertion[ParseSource]]]:
    return [
        (Arguments('', []), asrt_source.is_at_end_of_line(num_source_lines)),
        (Arguments('', ['following line']), asrt_source.is_at_end_of_line(num_source_lines)),
        (Arguments('', ['  ']), asrt_source.is_at_end_of_line(num_source_lines)),
    ]


def _equivalent_source_variants_for_consume_until_end_of_last_line(
        num_expression_lines: int = 1
) -> List[Tuple[List[str], ValueAssertion[ParseSource]]]:
    source_expectation = asrt_source.is_at_end_of_line(num_expression_lines)
    return [
        ([],
         source_expectation),

        (['non-empty following line'],
         source_expectation),

        (['     '],
         source_expectation),
        (['     ', 'non-empty-line'],
         source_expectation),
    ]


def _source_variants_with__for_expression_parser(num_expression_lines: int = 1
                                                 ) -> List[Tuple[Arguments, ValueAssertion[ParseSource]]]:
    space = '  '
    following_argument = 'argumentOfOthers'
    return [
        (Arguments('', []), asrt_source.is_at_end_of_line(num_expression_lines)),

        (Arguments(space, ['following line']),
         asrt_source.assert_source(current_line_number=asrt.equals(num_expression_lines),
                                   remaining_part_of_current_line=asrt.equals(space[1:]))),

        (Arguments(space + following_argument, ['  ']),
         asrt_source.assert_source(current_line_number=asrt.equals(num_expression_lines),
                                   remaining_part_of_current_line=asrt.equals(space[1:] + following_argument))),
    ]


def _source_variants_with__for_full_line_expression_parser(num_expression_lines: int = 1
                                                           ) -> List[Tuple[List[str], ValueAssertion[ParseSource]]]:
    source_expectation = asrt_source.is_at_end_of_line(num_expression_lines)
    return [
        ([], source_expectation),
        (['  '], source_expectation),
        (['following line'], source_expectation),
    ]


def _remaining_source__original_plus_extra_lines(original: str,
                                                 extra_lines: List[str]) -> ParseSource:
    return remaining_source('\n'.join([original] + extra_lines))


_SOURCE_VARIANT_TEST_CASES = _source_variant_test_cases__multi_line(1)
