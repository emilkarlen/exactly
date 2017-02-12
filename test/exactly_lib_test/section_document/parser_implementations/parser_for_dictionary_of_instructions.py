import unittest

from exactly_lib.section_document import model
from exactly_lib.section_document.parser_implementations import parser_for_dictionary_of_instructions as sut
from exactly_lib_test.section_document.test_resources.assertions import assert_equals_line
from exactly_lib_test.test_resources.parse import source3


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingNameExtractor))
    ret_val.addTest(unittest.makeSuite(TestParse))
    return ret_val


def name_extractor(s: str) -> str:
    return s[0]


class SingleInstructionParserThatRaisesInvalidArgumentError(sut.NamedInstructionParser):
    def __init__(self, error_message: str):
        self.error_message = error_message

    def apply(self, source: sut.SingleInstructionParserSource2) -> model.Instruction:
        raise sut.SingleInstructionInvalidArgumentException(self.error_message)


class SingleInstructionParserThatRaisesImplementationException(sut.NamedInstructionParser):
    def apply(self, source: sut.SingleInstructionParserSource2) -> model.Instruction:
        raise NotImplementedError()


class SingleInstructionParserThatSucceeds(sut.NamedInstructionParser):
    def apply(self, source: sut.SingleInstructionParserSource2) -> model.Instruction:
        source.source.consume_current_line()
        return Instruction(source.instruction_argument)


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
        phase_parser = sut.InstructionParserForDictionaryOfInstructions(splitter, {})
        source = source3(['line'])
        with self.assertRaises(sut.InvalidInstructionSyntaxException) as cm:
            phase_parser.parse(source)
            assert_equals_line(self,
                               source.current_line,
                               cm.ex.line,
                               'Source line')


class TestParse(unittest.TestCase):
    def test__when__instruction_name_not_in_dict__then__exception_should_be_raised(self):
        phase_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor, {})
        source = source3(['Ia'])
        with self.assertRaises(sut.UnknownInstructionException) as cm:
            phase_parser.parse(source)
            self.assertEqual('I',
                             cm.ex.instruction_name,
                             'Instruction name')
            assert_equals_line(self,
                               source.current_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_fails_to_parse_instruction_name_not_in_dict__then__exception_should_be_raised(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                        parsers_dict)
        source = source3(['Fa'])
        with self.assertRaises(sut.InvalidInstructionArgumentException) as cm:
            phase_parser.parse(source)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertEqual('the error message',
                             cm.ex.error_message,
                             'Error message')
            assert_equals_line(self,
                               source.current_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_raises_unknown_exception__then__exception_should_be_raised(self):
        parser_that_raises_exception = SingleInstructionParserThatRaisesImplementationException()
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': parser_that_raises_exception}
        phase_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                        parsers_dict)
        source = source3(['Fa'])
        with self.assertRaises(sut.ArgumentParsingImplementationException) as cm:
            phase_parser.parse(source)
            self.assertEqual('F',
                             cm.ex.instruction_name,
                             'Instruction name')
            self.assertIs(parser_that_raises_exception,
                          cm.ex.parser_that_raised_exception,
                          'Failing Parser instance')
            assert_equals_line(self,
                               source.current_line,
                               cm.ex.line,
                               'Source line')

    def test__when__parser_succeeds__then__the_instruction_should_be_returned(self):
        parsers_dict = {'S': SingleInstructionParserThatSucceeds(),
                        'F': SingleInstructionParserThatRaisesInvalidArgumentError('the error message')}
        phase_parser = sut.InstructionParserForDictionaryOfInstructions(name_extractor,
                                                                        parsers_dict)
        source = source3(['Sa'])
        instruction = phase_parser.parse(source)
        self.assertIsInstance(instruction,
                              Instruction,
                              'Instruction class')
        assert isinstance(instruction, Instruction)
        self.assertEqual(instruction.argument,
                         'a',
                         'Argument given to parser')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
