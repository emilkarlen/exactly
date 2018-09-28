import unittest
from typing import Any, Sequence

from exactly_lib.util.line_source import Line, LineSequence, line_sequence_from_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def equals_line(expected: Line) -> ValueAssertion[Any]:
    return asrt.is_instance_with(Line,
                                 asrt.And([
                                     asrt.sub_component('line_number',
                                                        Line.line_number.fget,
                                                        asrt.equals(expected.line_number)),
                                     asrt.sub_component('text',
                                                        Line.text.fget,
                                                        asrt.equals(expected.text))
                                 ]))


def is_line(description: str = '') -> ValueAssertion[Any]:
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


def is_line_sequence(description: str = '') -> ValueAssertion[Any]:
    return asrt.is_instance_with(LineSequence,
                                 asrt.And([
                                     asrt.sub_component('line_number',
                                                        LineSequence.first_line_number.fget,
                                                        asrt.is_instance(int)),
                                     asrt.sub_component_list('lines',
                                                             LineSequence.lines.fget,
                                                             asrt.is_instance(str))
                                 ]),
                                 description)


def matches_line_sequence(first_line_number: ValueAssertion[int] = asrt.anything_goes(),
                          lines: ValueAssertion[Sequence[str]] = asrt.anything_goes(),
                          ) -> ValueAssertion[LineSequence]:
    return asrt.is_instance_with(LineSequence,
                                 asrt.and_([
                                     asrt.sub_component('first_line_number',
                                                        LineSequence.first_line_number.fget,
                                                        first_line_number),
                                     asrt.sub_component('lines',
                                                        LineSequence.lines.fget,
                                                        lines),
                                 ]))


def equals_line_sequence(expected: LineSequence) -> ValueAssertion[LineSequence]:
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
