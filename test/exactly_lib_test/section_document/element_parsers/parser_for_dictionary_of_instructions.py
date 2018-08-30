import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers import parser_for_dictionary_of_instructions as sut
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import source_of_lines
from exactly_lib_test.util.test_resources.line_source_assertions import assert_equals_single_line


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingNameExtractor))
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


def name_extractor(s: str) -> str:
    return s[0]


class SingleInstructionParserThatRaisesInvalidArgumentError(sut.InstructionParser):
    def __init__(self, error_message: str):
        self.error_message = error_message

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: sut.ParseSource) -> model.Instruction:
        raise sut.SingleInstructionInvalidArgumentException(self.error_message)


class SingleInstructionParserThatRaisesImplementationException(sut.InstructionParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: sut.ParseSource) -> model.Instruction:
        raise NotImplementedError()


class SingleInstructionParserThatSucceeds(sut.InstructionParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: sut.ParseSource) -> model.Instruction:
        ret_val = Instruction(source.remaining_part_of_current_line)
        source.consume_current_line()
        return ret_val


class Instruction(model.Instruction):
    def __init__(self, argument: str):
        self.argument = argument


class TestFailingNameExtractor(unittest.TestCase):
    def test_parser_that_raises_exception(self):
        def extractor(x):
            raise NotImplementedError()

        self._check(extractor)

    def test_extractor_that_do_not_return_string(self):
        self._check(lambda x: 1)

    def test_extractor_that_do_not_take_a_single_argument(self):
        def extractor():
            return 'a'

        self._check(extractor)

    def _check(self, splitter):
        section_parser = sut.InstructionParserForDictionaryOfInstructions(splitter, {})
        source = source_of_lines(['line'])
        remaining_source_before = source.remaining_source
        with self.assertRaises(sut.InvalidInstructionSyntaxException) as cm:
            section_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        self.assertEqual(remaining_source_before,
                         source.remaining_source,
                         'source should not be consumed')
        assert_equals_single_line(self,
                                  source.current_line,
                                  cm.exception.source,
                                  'Source line')


class TestParse(unittest.TestCase):
    def test__when__instruction_name_not_in_dict__then__exception_should_be_raised(self):
        section_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor, {})
        source = source_of_lines(['Ia'])
        remaining_source_before = source.remaining_source

        with self.assertRaises(sut.UnknownInstructionException) as cm:
            section_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        self.assertEqual('I',
                         cm.exception.instruction_name,
                         'Instruction name')
        self.assertEqual(remaining_source_before,
                         source.remaining_source,
                         'source should not be consumed')
        assert_equals_single_line(self,
                                  source.current_line,
                                  cm.exception.source,
                                  'Source line')

    def test__when__parser_fails_to_parse_instruction_name_not_in_dict__then__exception_should_be_raised(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        section_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                          parsers_dict)
        source = source_of_lines(['Fa'])
        with self.assertRaises(sut.InvalidInstructionArgumentException) as cm:
            section_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        self.assertEqual('F',
                         cm.exception.instruction_name,
                         'Instruction name')
        self.assertEqual('the error message',
                         cm.exception.error_message,
                         'Error message')
        assert_equals_single_line(self,
                                  source.current_line,
                                  cm.exception.source,
                                  'Source line')

    def test__when__parser_raises_unknown_exception__then__exception_should_be_raised(self):
        parser_that_raises_exception = SingleInstructionParserThatRaisesImplementationException()
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': parser_that_raises_exception}
        section_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                          parsers_dict)
        source = source_of_lines(['Fa'])
        with self.assertRaises(sut.ArgumentParsingImplementationException) as cm:
            section_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
        self.assertEqual('F',
                         cm.exception.instruction_name,
                         'Instruction name')
        self.assertIs(parser_that_raises_exception,
                      cm.exception.parser_that_raised_exception,
                      'Failing Parser instance')
        assert_equals_single_line(self,
                                  source.current_line,
                                  cm.exception.source,
                                  'Source line')

    def test__when__parser_succeeds__then__the_instruction_should_be_returned(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        section_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                          parsers_dict)
        test_cases = [
            (['Sa'], 'a', ''),
            (['S  a'], 'a', ''),
            (['S  '], '', ''),
            (['S  ',
              'next line'], '', 'next line'),
        ]
        for source_lines, expected_argument, expected_remaining_source in test_cases:
            with self.subTest(source_lines=source_lines):
                source = source_of_lines(source_lines)
                instruction = section_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
                self.assertIsInstance(instruction,
                                      model.Instruction,
                                      'Instruction class')
                assert isinstance(instruction, Instruction)
                self.assertEqual(instruction.argument,
                                 expected_argument,
                                 'Argument given to parser')
                self.assertEqual(expected_remaining_source, source.remaining_source,
                                 'remaining_source')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
