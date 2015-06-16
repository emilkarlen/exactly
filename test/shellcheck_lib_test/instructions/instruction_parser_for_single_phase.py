import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib.instructions import instruction_parser_for_single_phase as parse
from shellcheck_lib.test_case import instructions
from shellcheck_lib_test.document.test_resources import assert_equals_line


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


def new_line(text: str) -> line_source.Line:
    return line_source.Line(1, text)


class TestFailingSplitter(unittest.TestCase):
    def test_parser_that_raises_exception(self):
        def parser(x):
            raise NotImplementedError()

        self._check(parser)

    def test_parser_that_do_not_return_pair(self):
        self._check(lambda x: x)

    def test_parser_that_do_not_take_a_single_argument(self):
        def parser():
            return 'a', 'b'

        self._check(parser)

    def _check(self,
               splitter):
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(splitter, {})
        line = new_line('line')
        with self.assertRaises(parse.InvalidInstructionSyntaxException) as cm:
            phase_parser.apply(line)
            assert_equals_line(self,
                               line,
                               cm.ex.line,
                               'Source line')


class TestParse(unittest.TestCase):
    def test__when__instruction_name_not_in_dict__then__exception_should_be_raised(self):
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

    def test__when__parser_fails_to_parse_instruction_name_not_in_dict__then__exception_should_be_raised(self):
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

    def test__when__parser_succeeds__then__the_instruction_should_be_returned(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = parse.InstructionParserForDictionaryOfInstructions(name_argument_splitter,
                                                                          parsers_dict)
        line = new_line('Sa')
        phase_content_element = phase_parser.apply(line)
        self.assertTrue(phase_content_element.is_instruction,
                        'Should be instruction')
        self.assertFalse(phase_content_element.is_comment,
                         'Should NOT be comment')
        assert_equals_line(self,
                           line,
                           phase_content_element.source_line,
                           'Source line')
        self.assertIsInstance(phase_content_element.instruction,
                              Instruction,
                              'Instruction class')
        self.assertEqual(phase_content_element.instruction.argument,
                         'a',
                         'Argument given to parser')


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
    ret_val.addTest(unittest.makeSuite(TestFailingSplitter))
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


if __name__ == '__main__':
    unittest.main()
