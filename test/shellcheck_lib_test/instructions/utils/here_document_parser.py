import shlex
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from shellcheck_lib.instructions.utils import here_document_parser as sut
from shellcheck_lib_test.instructions.test_resources.utils import multi_line_source


class TestFailingScenarios(unittest.TestCase):
    def test_fail_when_document_is_mandatory_but_is_not_given(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = []
            sut.parse_as_last_argument(True,
                                       first_line_arguments,
                                       new_source(first_line_arguments))

    def test_fail_when_superfluous_arguments__document_is_mandatory(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER', 'superfluous argument']
            sut.parse_as_last_argument(True,
                                       first_line_arguments,
                                       new_source(first_line_arguments))

    def test_fail_when_superfluous_arguments__document_is_not_mandatory(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER', 'superfluous argument']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       new_source(first_line_arguments))

    def test_fail_when_marker_not_found(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       new_source(first_line_arguments,
                                                  ['not marker',
                                                   '[section]']))


class TestSuccessfulScenarios(unittest.TestCase):
    def test_empty_list_of_lines__not_mandatory(self):
        first_line_arguments = ['<<MARKER']
        source = new_source(first_line_arguments, ['MARKER'])
        actual = sut.parse_as_last_argument(False,
                                            first_line_arguments,
                                            source)
        self.assertEquals([],
                          actual)
        self.assertFalse(source.line_sequence.has_next())

    def test_empty_list_of_lines__mandatory(self):
        first_line_arguments = ['<<___']
        source = new_source(first_line_arguments, ['___'])
        actual = sut.parse_as_last_argument(True,
                                            first_line_arguments,
                                            source)
        self.assertEquals([],
                          actual)
        self.assertFalse(source.line_sequence.has_next())

    def test_single_line__not_mandatory(self):
        first_line_arguments = ['<<MARKER']
        source = new_source(first_line_arguments,
                            ['only line',
                             'MARKER',
                             'following line'])
        actual = sut.parse_as_last_argument(False,
                                            first_line_arguments,
                                            source)
        self.assertEquals(['only line'],
                          actual)
        self.assertTrue(source.line_sequence.has_next())
        self.assertEqual('following line',
                         source.line_sequence.next_line())

    def test_single_line__mandatory(self):
        first_line_arguments = ['<<123']
        source = new_source(first_line_arguments, ['only line', '123'])
        actual = sut.parse_as_last_argument(True,
                                            first_line_arguments,
                                            source)
        self.assertEquals(['only line'],
                          actual)
        self.assertFalse(source.line_sequence.has_next())


def new_source(arguments: list,
               following_lines: iter=()) -> SingleInstructionParserSource:
    return multi_line_source(' '.join(map(shlex.quote, arguments)),
                             following_lines)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
