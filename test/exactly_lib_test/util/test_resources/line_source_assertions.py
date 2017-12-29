import unittest
from typing import Any, Sequence

from exactly_lib.util.line_source import Line, LineSequence, SourceLocation, SourceLocationPath
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_line(expected: Line) -> asrt.ValueAssertion[Any]:
    return asrt.is_instance_with(Line,
                                 asrt.And([
                                     asrt.sub_component('line_number',
                                                        Line.line_number.fget,
                                                        asrt.equals(expected.line_number)),
                                     asrt.sub_component('text',
                                                        Line.text.fget,
                                                        asrt.equals(expected.text))
                                 ]))


def is_line(description: str = '') -> asrt.ValueAssertion[Any]:
    return asrt.is_instance_with(Line,
                                 asrt.And([
                                     asrt.sub_component('line_number',
                                                        Line.line_number.fget,
                                                        asrt.is_instance(int)),
                                     asrt.sub_component('text',
                                                        Line.text.fget,
                                                        asrt.is_instance(str))
                                 ]),
                                 description)


def equals_line_sequence(expected: LineSequence) -> asrt.ValueAssertion[LineSequence]:
    return asrt.and_([
        asrt.sub_component('first_line_number',
                           LineSequence.first_line_number.fget,
                           asrt.equals(expected.first_line_number)),
        asrt.sub_component('lines',
                           LineSequence.lines.fget,
                           asrt.equals_sequence(expected.lines,
                                                asrt.equals)),
    ])


def assert_equals_line(test_case: unittest.TestCase,
                       expected: Line,
                       actual: Line,
                       message_header: str = None):
    """
    :param expected: May be None
    :param actual: May be None
    :param message_header: Optional header for assert messages.
    """
    if expected is None:
        assertion = asrt.is_none
    else:
        assertion = equals_line(expected)
    message_builder = asrt.MessageBuilder('' if message_header is None else message_header)

    assertion.apply(test_case, actual, message_builder)


def equals_source_location(expected: SourceLocation) -> asrt.ValueAssertion[SourceLocation]:
    return asrt.is_instance_with(SourceLocation,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        SourceLocation.source.fget,
                                                        equals_line_sequence(expected.source)),
                                     asrt.sub_component('file_path',
                                                        SourceLocation.file_path.fget,
                                                        asrt.equals(expected.file_path)),
                                 ]))


def equals_source_location_sequence(expected: Sequence[SourceLocation]
                                    ) -> asrt.ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence(list(map(equals_source_location,
                                          expected)))


def equals_source_location_path(expected: SourceLocationPath) -> asrt.ValueAssertion[SourceLocationPath]:
    return asrt.is_instance_with(SourceLocationPath,
                                 asrt.and_([
                                     asrt.sub_component('location',
                                                        SourceLocationPath.location.fget,
                                                        equals_source_location(expected.location)),
                                     asrt.sub_component('file_inclusion_chain',
                                                        SourceLocationPath.file_inclusion_chain.fget,
                                                        equals_source_location_sequence(expected.file_inclusion_chain)),
                                 ]))
