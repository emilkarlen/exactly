import argparse
import unittest

from exactly_lib.document import parse
from exactly_lib.document.model import Instruction
from exactly_lib.document.parse import LineSequenceSourceFromListOfLines, ListOfLines
from exactly_lib.document.parser_implementations import instruction_parser_using_argument_parser as sut
from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.util import line_source


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


def new_source(text: str) -> line_source.LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines([])),
        1,
        text)


class InstructionWithInteger(Instruction):
    def __init__(self, value):
        self.value = value


class Parser(sut.SingleLineParser):
    def __init__(self):
        parser = argparse.ArgumentParser(description='Test parser')
        parser.add_argument('integer', metavar='N', type=int)
        super().__init__(parser)

    def _new_instruction_from(self, namespace: argparse.Namespace) -> InstructionWithInteger:
        return InstructionWithInteger(namespace.integer)


class ParserThatRaisesUnconditionallyWhenConstructingInstruction(sut.SingleLineParser):
    def __init__(self,
                 error_message: str):
        self.error_message = error_message
        parser = argparse.ArgumentParser(description='Test parser')
        parser.add_argument('integer', metavar='N', type=int)
        super().__init__(parser)

    def _new_instruction_from(self, namespace: argparse.Namespace) -> InstructionWithInteger:
        raise SingleInstructionInvalidArgumentException(self.error_message)


class TestParse(unittest.TestCase):
    def test__when__argument_is_invalid__then__exception_should_be_raised(self):
        parser = Parser()
        with self.assertRaises(sut.SingleInstructionInvalidArgumentException) as cm:
            parser.apply(source('not an integer'))

    def test__exception_from_instruction_construction(self):
        parser = ParserThatRaisesUnconditionallyWhenConstructingInstruction('error message')
        with self.assertRaises(sut.SingleInstructionInvalidArgumentException) as cm:
            parser.apply(source('28'))
            self.assertEqual('error message',
                             cm.ex.error_message,
                             'Error message in exception')

    def test__when__argument_is_valid__then__an_instruction_initialized_from_this_argument_should_be_returned(self):
        parser = Parser()
        instruction = parser.apply(source('43'))
        self.assertEqual(43, instruction.value)


def source(instruction_argument: str) -> SingleInstructionParserSource:
    return SingleInstructionParserSource(
        line_source.LineSequenceBuilder(LineSequenceSourceFromListOfLines(ListOfLines(['first line'])),
                                        1,
                                        'first line'),
        instruction_argument)


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
