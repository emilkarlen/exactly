import pathlib
import unittest
from typing import Any, Sequence

from exactly_lib.util.line_source import Line, LineSequence, SourceLocation, SourceLocationPath, line_sequence_from_line
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


def matches_line_sequence(first_line_number: asrt.ValueAssertion[int] = asrt.anything_goes(),
                          lines: asrt.ValueAssertion[Sequence[str]] = asrt.anything_goes(),
                          ) -> asrt.ValueAssertion[LineSequence]:
    return asrt.is_instance_with(LineSequence,
                                 asrt.and_([
                                     asrt.sub_component('first_line_number',
                                                        LineSequence.first_line_number.fget,
                                                        first_line_number),
                                     asrt.sub_component('lines',
                                                        LineSequence.lines.fget,
                                                        lines),
                                 ]))


def equals_line_sequence(expected: LineSequence) -> asrt.ValueAssertion[LineSequence]:
    return matches_line_sequence(first_line_number=asrt.equals(expected.first_line_number),
                                 lines=asrt.equals_sequence(expected.lines,
                                                            asrt.equals))


def assert_equals_line_sequence(put: unittest.TestCase,
                                expected: LineSequence,
                                actual: LineSequence,
                                msg: str = 'line sequence'):
    assertion = equals_line_sequence(expected)
    assertion.apply_with_message(put, actual, msg)


def assert_equals_single_line(test_case: unittest.TestCase,
                              expected: Line,
                              actual: LineSequence,
                              message_header: str = None):
    """
    :param expected: May be None
    :param actual: May be None
    :param message_header: Optional header for assert messages.
    """
    if expected is None:
        assertion = asrt.is_none
    else:
        assertion = equals_line_sequence(line_sequence_from_line(expected))
    message_builder = asrt.MessageBuilder('' if message_header is None else message_header)

    assertion.apply(test_case, actual, message_builder)


def matches_source_location(source: asrt.ValueAssertion[LineSequence] = asrt.anything_goes(),
                            file_path: asrt.ValueAssertion[pathlib.Path] = asrt.anything_goes(),
                            ) -> asrt.ValueAssertion[SourceLocation]:
    return asrt.is_instance_with(SourceLocation,
                                 asrt.and_([
                                     asrt.sub_component('source',
                                                        SourceLocation.source.fget,
                                                        source),
                                     asrt.sub_component('file_path',
                                                        SourceLocation.file_path.fget,
                                                        file_path),
                                 ]))


def equals_source_location(expected: SourceLocation) -> asrt.ValueAssertion[SourceLocation]:
    return matches_source_location(source=equals_line_sequence(expected.source),
                                   file_path=asrt.equals(expected.file_path))


def equals_source_location_sequence(expected: Sequence[SourceLocation]
                                    ) -> asrt.ValueAssertion[Sequence[SourceLocation]]:
    return asrt.matches_sequence(list(map(equals_source_location,
                                          expected)))


def matches_source_location_path(source_location: asrt.ValueAssertion[SourceLocation] = asrt.anything_goes(),
                                 file_inclusion_chain: asrt.ValueAssertion[
                                     Sequence[SourceLocation]] = asrt.anything_goes(),
                                 ) -> asrt.ValueAssertion[SourceLocationPath]:
    return asrt.is_instance_with(SourceLocationPath,
                                 asrt.and_([
                                     asrt.sub_component('location',
                                                        SourceLocationPath.location.fget,
                                                        source_location),
                                     asrt.sub_component('file_inclusion_chain',
                                                        SourceLocationPath.file_inclusion_chain.fget,
                                                        file_inclusion_chain),
                                 ]))


def equals_source_location_path(expected: SourceLocationPath) -> asrt.ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=equals_source_location(expected.location),
        file_inclusion_chain=equals_source_location_sequence(expected.file_inclusion_chain))


def equals_single_line_source_location_path(expected: Line) -> asrt.ValueAssertion[SourceLocationPath]:
    return matches_source_location_path(
        source_location=matches_source_location(
            source=matches_line_sequence(
                first_line_number=asrt.equals(expected.line_number),
                lines=asrt.matches_sequence([asrt.equals(expected.text)])),
            file_path=asrt.is_none),
        file_inclusion_chain=equals_source_location_sequence([]))
