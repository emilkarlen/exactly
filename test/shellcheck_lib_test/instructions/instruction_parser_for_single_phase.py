import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib.instructions import instruction_parser_for_single_phase as parse
from shellcheck_lib.test_case import instructions
from shellcheck_lib_test.document.test_resources import assert_equals_line


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


def new_line(text: str) -> line_source.Line:
    return line_source.Line(1, text)


class TestParse(unittest.TestCase):
    def test_when_instruction_name_not_in_dict_then_exception_should_be_raised(self):
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(name_argument_splitter, {})
        line = new_line('Ia')
        with self.assertRaises(parse.UnknownInstructionException) as cm:
            phase_parser.apply(line)
            self.assertEqual('I',
                             cm.ex.instruction_name,
                             'Instruction name')
            assert_equals_line(self,
                               line,
                               cm.ex.line,
                               'Source line')

    def test_when_parser_fails_to_parse_instruction_name_not_in_dict_then_exception_should_be_raised(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(name_argument_splitter,
                                                                          parsers_dict)
        line = new_line('Fa')
        with self.assertRaises(parse.InvalidInstructionArgumentException) as cm:
            phase_parser.apply(line)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertEqual('the error message',
                             cm.ex.error_message,
                             'Error message')
            assert_equals_line(self,
                               line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_raises_unknown_exception__then__exception_should_be_raised(self):
        parser_that_raises_exception = SingleInstructionParserThatRaisesImplementationException()
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': parser_that_raises_exception}
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(name_argument_splitter,
                                                                          parsers_dict)
        line = new_line('Fa')
        with self.assertRaises(parse.ArgumentParsingImplementationException) as cm:
            phase_parser.apply(line)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertIs(parser_that_raises_exception,
                          cm.ex.parser_that_raised_exception,
                          'Failing Parser instance')
            assert_equals_line(self,
                               line,
                               cm.ex.line,
                               'Source line')

# def test_handling_of_invalid_argument_exception_from_parser(self):
# parser = exitcode.Parser()
# self.assertRaises(parse.SingleInstructionInvalidArgumentException,
#                           parser.apply,
#                           '')


class SingleInstructionParserThatRaisesInvalidArgumentError(parse.SingleInstructionParser):
    def __init__(self,
                 error_message: str):
        self.error_message = error_message

    def apply(self, instruction_argument: str) -> instructions.Instruction:
        raise parse.SingleInstructionInvalidArgumentException(self.error_message)


class SingleInstructionParserThatRaisesImplementationException(parse.SingleInstructionParser):
    def apply(self, instruction_argument: str) -> instructions.Instruction:
        raise NotImplementedError()


class SingleInstructionParserThatSucceeds(parse.SingleInstructionParser):
    def apply(self, instruction_argument: str) -> instructions.Instruction:
        return Instruction(instruction_argument)


class Instruction(instructions.Instruction):
    def __init__(self,
                 argument: str):
        self.argument = argument


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


if __name__ == '__main__':
    unittest.main()
