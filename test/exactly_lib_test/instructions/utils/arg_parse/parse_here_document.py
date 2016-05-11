import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_document as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.test_resources.parse import argument_list_source


class TestFailingScenarios(unittest.TestCase):
    def test_fail_when_document_is_mandatory_but_is_not_given(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = []
            sut.parse_as_last_argument(True,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments))

    def test_fail_when_superfluous_arguments__document_is_mandatory(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER', 'superfluous argument']
            sut.parse_as_last_argument(True,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments))

    def test_fail_when_superfluous_arguments__document_is_not_mandatory(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER', 'superfluous argument']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments))

    def test_fail_when_marker_not_found(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments,
                                                            ['not marker',
                                                             '[section]']))

    def test_fail_when_marker_not_found__must_match_whole_line__space_before(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments,
                                                            ['  MARKER']))

    def test_fail_when_marker_not_found__must_match_whole_line__space_after(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            first_line_arguments = ['<<MARKER']
            sut.parse_as_last_argument(False,
                                       first_line_arguments,
                                       argument_list_source(first_line_arguments,
                                                            ['MARKER  ']))


class TestSuccessfulScenarios(unittest.TestCase):
    def test_empty_list_of_lines__not_mandatory(self):
        first_line_arguments = ['<<MARKER']
        source = argument_list_source(first_line_arguments, ['MARKER'])
        actual = sut.parse_as_last_argument(False,
                                            first_line_arguments,
                                            source)
        self.assertEquals([],
                          actual)
        self.assertFalse(source.line_sequence.has_next())

    def test_empty_list_of_lines__mandatory(self):
        first_line_arguments = ['<<___']
        source = argument_list_source(first_line_arguments, ['___'])
        actual = sut.parse_as_last_argument(True,
                                            first_line_arguments,
                                            source)
        self.assertEquals([],
                          actual)
        self.assertFalse(source.line_sequence.has_next())

    def test_single_line__not_mandatory(self):
        first_line_arguments = ['<<MARKER']
        source = argument_list_source(first_line_arguments,
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
        source = argument_list_source(first_line_arguments, ['only line', '123'])
        actual = sut.parse_as_last_argument(True,
                                            first_line_arguments,
                                            source)
        self.assertEquals(['only line'],
                          actual)
        self.assertFalse(source.line_sequence.has_next())


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenarios))
    return ret_val


if __name__ == '__main__':
    unittest.main()
