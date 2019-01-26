import unittest

from typing import List, Tuple, Iterator

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import every_line_is_consumed, \
    is_at_beginning_of_line
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equivalent_source_variants__with_source_check(put: unittest.TestCase,
                                                  instruction_argument: str):
    """
    Yields a ParseSource

    Checks that the first line of the source has been consumed.

    Assumes that the body of the loop parses using the given source.
    """
    num_source_lines = len(instruction_argument.split('\n'))
    for following_lines, source_assertion in _source_variant_test_cases__multi_line(num_source_lines):
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants__with_source_check__multi_line(put: unittest.TestCase,
                                                              instruction_argument: Arguments):
    """
    Yields a ParseSource

    Checks that the first line of the source has been consumed.

    Assumes that the body of the loop parses using the given source.
    """
    for following_lines, source_assertion in _source_variant_test_cases__multi_line(instruction_argument.num_lines):
        with put.subTest(following_lines=repr(following_lines)):
            source = instruction_argument.followed_by_lines(following_lines).as_remaining_source
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants__with_source_check__following_content_on_last_line_accepted(
        put: unittest.TestCase,
        original_arguments: Arguments):
    """
    Yields a ParseSource

    Checks that the first line of the source has been consumed.

    Assumes that the body of the loop parses using the given source.
    """
    for following_arguments, source_assertion in _source_variants_with_accepted_following_content_on_same_line(
            original_arguments.num_lines):
        with put.subTest(additional_arguments_on_same_line=repr(following_arguments.first_line),
                         additional_lines=repr(following_arguments.following_lines)):
            source = original_arguments.last_line_followed_by(following_arguments,
                                                              first_line_separator='').as_remaining_source
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants(put: unittest.TestCase,
                               instruction_argument: str) -> Iterator[ParseSource]:
    """
    Yields a ParseSource
    """
    for following_lines, source_assertion in _SOURCE_VARIANT_TEST_CASES:
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source


def equivalent_source_variants_with_assertion(put: unittest.TestCase,
                                              instruction_argument: str):
    """
    Yields a ParseSource, ValueAssertion
    """
    for following_lines, source_assertion in _SOURCE_VARIANT_TEST_CASES:
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source, source_assertion


def _source_variant_test_cases__multi_line(num_source_lines: int
                                           ) -> List[Tuple[List[str], ValueAssertion[ParseSource]]]:
    return [
        ([], every_line_is_consumed),
        (['following line'], is_at_beginning_of_line(num_source_lines + 1)),
        (['  '], is_at_beginning_of_line(num_source_lines + 1)),
    ]


def _source_variants_with_accepted_following_content_on_same_line(
        num_source_lines: int
) -> List[Tuple[Arguments, ValueAssertion[ParseSource]]]:
    return [
        (Arguments('', []), asrt_source.is_at_end_of_line(num_source_lines)),
        (Arguments('', ['following line']), asrt_source.is_at_end_of_line(num_source_lines)),
        (Arguments('', ['  ']), asrt_source.is_at_end_of_line(num_source_lines)),
    ]


_SOURCE_VARIANT_TEST_CASES = _source_variant_test_cases__multi_line(1)
