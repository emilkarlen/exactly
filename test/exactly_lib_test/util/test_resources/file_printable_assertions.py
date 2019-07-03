import unittest

from exactly_lib.util import file_printables
from exactly_lib.util.file_printer import FilePrintable
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, MessageBuilder


def matches(output: ValueAssertion[str] = asrt.anything_goes()) -> ValueAssertion[FilePrintable]:
    return _FilePrintableMatches(output)


def equals_string(output: str) -> ValueAssertion[FilePrintable]:
    return _FilePrintableMatches(asrt.equals(output))


def equals(expected: FilePrintable) -> ValueAssertion[FilePrintable]:
    return _FilePrintableMatches(asrt.equals(file_printables.print_to_string(expected)))


class _FilePrintableMatches(asrt.ValueAssertionBase[FilePrintable]):
    def __init__(self, output: ValueAssertion[str]):
        self.output = output

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: MessageBuilder):
        put.assertIsInstance(value, FilePrintable,
                             message_builder.apply('type'))

        actual_output = file_printables.print_to_string(value)

        self.output.apply(put,
                          actual_output,
                          message_builder.for_sub_component('rendered-string'))
