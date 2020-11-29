import unittest
from typing import List, Tuple, Iterator, TypeVar

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.test_utils import NEA, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equivalent_source_variants__with_source_check__consume_last_line(put: unittest.TestCase,
                                                                     instruction_argument: str,
                                                                     ) -> Iterator[ParseSource]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    instruction_argument = instruction_argument.rstrip('\n')
    num_source_lines = len(instruction_argument.split('\n'))
    for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines):
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants__with_source_check__consume_last_line_2(
        instruction_argument: str,
) -> List[Tuple[ParseSource, ValueAssertion[ParseSource]]]:
    """
    Checks that the whole instruction_argument has been consumed,
    and that the parser is positioned at the beginning of the following line.

    Assumes that the body of the loop parses using the given source.
    """
    num_source_lines = len(instruction_argument.split('\n'))
    return [
        (
            remaining_source(instruction_argument, following_lines),
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
) -> List[Tuple[ParseSource, ValueAssertion[ParseSource]]]:
    return [
        (
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


def equivalent_source_variants__with_source_check__for_expression_parser(
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


def equivalent_source_variants__with_source_check__for_expression_parser_2(
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


_SOURCE_VARIANT_TEST_CASES = _source_variant_test_cases__multi_line(1)
