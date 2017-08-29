import unittest

from exactly_lib_test.section_document.test_resources.parse_source_assertions import every_line_is_consumed, \
    is_at_beginning_of_line
from exactly_lib_test.test_resources.parse import remaining_source


def equivalent_source_variants__with_source_check(put: unittest.TestCase,
                                                  instruction_argument: str):
    """
    Yields a ParseSource

    Checks that the first line of the source has been consumed.

    Assumes that the body of the loop parses using the given source.
    """
    for following_lines, source_assertion in _SOURCE_VARIANT_TEST_CASES:
        with put.subTest(following_lines=repr(following_lines)):
            source = remaining_source(instruction_argument, following_lines)
            yield source
            source_assertion.apply_with_message(put, source, 'source after parse')


def equivalent_source_variants(put: unittest.TestCase,
                               instruction_argument: str):
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


_SOURCE_VARIANT_TEST_CASES = [
    ([], every_line_is_consumed),
    (['following line'], is_at_beginning_of_line(2)),
    (['  '], is_at_beginning_of_line(2)),
]
