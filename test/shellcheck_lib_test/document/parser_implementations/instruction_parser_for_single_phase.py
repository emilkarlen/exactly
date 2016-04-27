import unittest

from exactly_lib.document import model
from exactly_lib.document import parse
from exactly_lib.document.model import ElementType
from exactly_lib.document.parser_implementations import instruction_parser_for_single_phase as sut
from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util import line_source
from exactly_lib.util.line_source import Line
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(splitter, {})
        source = new_source('line')
        with self.assertRaises(sut.InvalidInstructionSyntaxException) as cm:
            phase_parser.apply(source)
            assert_equals_line(self,
                               source.first_line,
                               cm.ex.line,
                               'Source line')


class TestParse(unittest.TestCase):
    def test__when__instruction_name_not_in_dict__then__exception_should_be_raised(self):
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter, {})
        source = new_source('Ia')
        with self.assertRaises(sut.UnknownInstructionException) as cm:
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                           parsers_dict)
        source = new_source('Fa')
        with self.assertRaises(sut.InvalidInstructionArgumentException) as cm:
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                           parsers_dict)
        source = new_source('Fa')
        with self.assertRaises(sut.ArgumentParsingImplementationException) as cm:
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
                                                                           parsers_dict)
        source = new_source('Sa')
        phase_content_element = phase_parser.apply(source)
        self.assertEqual(ElementType.INSTRUCTION,
                         phase_content_element.element_type,
                         'Should be instruction')
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
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
        phase_parser = sut.SectionElementParserForDictionaryOfInstructions(name_argument_splitter,
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


class TestSectionElementParserForStandardCommentAndEmptyLines(unittest.TestCase):
    def test_parse_empty_line(self):
        parser = SectionElementParserForStandardCommentAndEmptyLines()
        source = new_source('')
        element = parser.apply(source)
        self.assertEqual(ElementType.EMPTY,
                         element.element_type,
                         'Element type')
        assert_equals_line(self,
                           Line(1, ''),
                           element.first_line)

    def test_parse_comment_line(self):
        parser = SectionElementParserForStandardCommentAndEmptyLines()
        source = new_source('# comment')
        element = parser.apply(source)
        self.assertEqual(ElementType.COMMENT,
                         element.element_type,
                         'Element type')
        assert_equals_line(self,
                           Line(1, '# comment'),
                           element.first_line)

    def test_parse_instruction_line(self):
        parser = SectionElementParserForStandardCommentAndEmptyLines()
        source = new_source('instruction')
        element = parser.apply(source)
        self.assertEqual(ElementType.INSTRUCTION,
                         element.element_type,
                         'Element type')
        self.assertIsInstance(element.instruction,
                              Instruction,
                              'Instruction class')
        assert_equals_line(self,
                           Line(1, 'instruction'),
                           element.first_line)


class SingleInstructionParserThatRaisesInvalidArgumentError(sut.SingleInstructionParser):
    def __init__(self,
                 error_message: str):
        self.error_message = error_message

    def apply(self, source: SingleInstructionParserSource) -> model.Instruction:
        raise sut.SingleInstructionInvalidArgumentException(self.error_message)


class SingleInstructionParserThatRaisesImplementationException(sut.SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> model.Instruction:
        raise NotImplementedError()


class SingleInstructionParserThatSucceeds(sut.SingleInstructionParser):
    def apply(self, source: SingleInstructionParserSource) -> model.Instruction:
        return Instruction(source.instruction_argument)


class SectionElementParserForStandardCommentAndEmptyLines(sut.SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> model.Instruction:
        return Instruction(source.first_line.text)


class Instruction(model.Instruction):
    def __init__(self,
                 argument: str):
        self.argument = argument


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingSplitter))
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestSectionElementParserForStandardCommentAndEmptyLines))
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
