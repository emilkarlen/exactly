import unittest

from shellcheck_lib.document.model import ElementType

from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.instructions import instruction_parser_for_single_phase as single_phase_parse
from shellcheck_lib.test_case import instructions
from shellcheck_lib_test.document.test_resources import assert_equals_line


def name_argument_splitter(s: str) -> (str, str):
    return s[0], s[1:]


def new_source(text: str) -> line_source.LineSequenceBuilder:
    return line_source.LineSequenceBuilder(
        parse.LineSequenceSourceFromListOfLines(
            parse.ListOfLines([])),
        1,
        text)


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
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(splitter, {})
        source = new_source('line')
        with self.assertRaises(single_phase_parse.InvalidInstructionSyntaxException) as cm:
            phase_parser.apply(source)
            assert_equals_line(self,
                               source.first_line,
                               cm.ex.line,
                               'Source line')


class TestParse(unittest.TestCase):
    def test__when__instruction_name_not_in_dict__then__exception_should_be_raised(self):
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter, {})
        source = new_source('Ia')
        with self.assertRaises(single_phase_parse.UnknownInstructionException) as cm:
            phase_parser.apply(source)
            self.assertEqual('I',
                             cm.ex.instruction_name,
                             'Instruction name')
            assert_equals_line(self,
                               source.first_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_fails_to_parse_instruction_name_not_in_dict__then__exception_should_be_raised(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                                          parsers_dict)
        source = new_source('Fa')
        with self.assertRaises(single_phase_parse.InvalidInstructionArgumentException) as cm:
            phase_parser.apply(source)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertEqual('the error message',
                             cm.ex.error_message,
                             'Error message')
            assert_equals_line(self,
                               source.first_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_raises_unknown_exception__then__exception_should_be_raised(self):
        parser_that_raises_exception = SingleInstructionParserThatRaisesImplementationException()
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': parser_that_raises_exception}
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                                          parsers_dict)
        source = new_source('Fa')
        with self.assertRaises(single_phase_parse.ArgumentParsingImplementationException) as cm:
            phase_parser.apply(source)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertIs(parser_that_raises_exception,
                          cm.ex.parser_that_raised_exception,
                          'Failing Parser instance')
            assert_equals_line(self,
                               source.first_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_succeeds__then__the_instruction_should_be_returned(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                                          parsers_dict)
        source = new_source('Sa')
        phase_content_element = phase_parser.apply(source)
        self.assertTrue(phase_content_element.is_instruction,
                        'Should be instruction')
        self.assertFalse(phase_content_element.is_comment,
                         'Should NOT be comment')
        assert_equals_line(self,
                           source.first_line,
                           phase_content_element.first_line,
                           'Source line')
        self.assertIsInstance(phase_content_element.instruction,
                              Instruction,
                              'Instruction class')
        self.assertEqual(phase_content_element.instruction.argument,
                         'a',
                         'Argument given to parser')

    def test__when__line_is_empty__then__an_empty_line_element_should_be_returned(self):
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                                          {})
        source = new_source('')
        phase_content_element = phase_parser.apply(source)
        self.assertEqual(phase_content_element.element_type,
                         ElementType.EMPTY,
                         'Element type')
        assert_equals_line(self,
                           source.first_line,
                           phase_content_element.first_line,
                           'Source line')

    def test__when__line_is_comment__then__a_comment_line_element_should_be_returned(self):
        phase_parser = single_phase_parse.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                                          {})
        source = new_source('# comment')
        phase_content_element = phase_parser.apply(source)
        self.assertEqual(phase_content_element.element_type,
                         ElementType.COMMENT,
                         'Element type')
        assert_equals_line(self,
                           source.first_line,
                           phase_content_element.first_line,
                           'Source line')


class SingleInstructionParserThatRaisesInvalidArgumentError(single_phase_parse.SingleInstructionParser):
    def __init__(self,
                 error_message: str):
        self.error_message = error_message

    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> instructions.Instruction:
        raise single_phase_parse.SingleInstructionInvalidArgumentException(self.error_message)


class SingleInstructionParserThatRaisesImplementationException(single_phase_parse.SingleInstructionParser):
    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> instructions.Instruction:
        raise NotImplementedError()


class SingleInstructionParserThatSucceeds(single_phase_parse.SingleInstructionParser):
    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> instructions.Instruction:
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
