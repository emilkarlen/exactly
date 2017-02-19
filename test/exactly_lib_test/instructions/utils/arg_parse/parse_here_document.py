import unittest

from exactly_lib.instructions.utils.arg_parse import parse_here_document as sut
from exactly_lib.section_document import syntax
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.section_document.parser_implementations.optional_description_and_instruction_parser import \
    source_is_at_end
from exactly_lib_test.section_document.test_resources.parse_source import source_is_not_at_end
from exactly_lib_test.test_resources.parse import argument_list_source, remaining_source, remaining_source_lines
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestFailingScenariosOld(unittest.TestCase):
    # TODO [instr-desc] Remove when new parser structures are fully integrated
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


class TestSuccessfulScenariosOld(unittest.TestCase):
    # TODO [instr-desc] Remove when new parser structures are fully integrated
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


class TestFailingScenarios(unittest.TestCase):
    def test_fail_when_document_is_mandatory_but_is_not_given(self):
        test_cases = [
            '',
            '    ',
        ]
        for first_line in test_cases:
            with self.subTest(msg='remaining source: ' + repr(first_line)):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    sut.parse_as_last_argumentInstrDesc(True,
                                                        remaining_source(first_line))

    def test_fail_when_invalid_here_document_argument(self):
        first_line_cases = [
            '<<MARKER superfluous_argument',
            '<<MARKER superfluous argument',
            '\'<<MARKER\'',
        ]
        test_cases = [
            False,
            True,
        ]
        for first_line in first_line_cases:
            for is_mandatory in test_cases:
                with self.subTest(msg='mandatory: ' + repr(is_mandatory)):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_as_last_argumentInstrDesc(is_mandatory,
                                                            remaining_source(first_line))

    def test_fail_when_end_marker_not_found(self):
        first_line = '<<MARKER'
        following_lines_cases = [
            [
                'not marker',
                syntax.section_header('section-name'),
            ],
            [
                'not marker',
            ],
            [],
            [
                '   MARKER',
            ],
            [
                'MARKER    ',
            ],
            [
                'NOTMARKER',
            ],
        ]
        for following_lines in following_lines_cases:
            for is_mandatory in [False, True]:
                with self.subTest(msg=repr((is_mandatory, following_lines))):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_as_last_argumentInstrDesc(is_mandatory,
                                                            remaining_source(first_line,
                                                                             following_lines))


class TestSuccessfulScenarios(unittest.TestCase):
    def test_here_document_is_given(self):
        source_cases = [
            ([
                 '<<MARKER',
                 'MARKER',
             ],
             [],
             source_is_at_end),
            ([
                 '<<eof',
                 'eof',
             ],
             [],
             source_is_at_end),
            ([
                 '<<MARKER',
                 'MARKER',
                 ' after',
             ],
             [],
             source_is_not_at_end(current_line_number=asrt.equals(3),
                                  remaining_part_of_current_line=asrt.equals(' after'))),
            ([
                 '<<eof',
                 'single line contents',
                 'eof',
             ],
             ['single line contents'],
             source_is_at_end),
            ([
                 '<<EOF',
                 'first line',
                 'second line',
                 'EOF',
                 'line after',
             ],
             ['first line',
              'second line',
              ],
             source_is_not_at_end(current_line_number=asrt.equals(5),
                                  remaining_part_of_current_line=asrt.equals('line after'))),
        ]
        for source_lines, expected_document_contents, source_assertion in source_cases:
            for is_mandatory in [False, True]:
                with self.subTest(msg=repr((source_lines, expected_document_contents, source_assertion))):
                    source = remaining_source_lines(source_lines)
                    actual = sut.parse_as_last_argumentInstrDesc(is_mandatory, source)
                    self.assertEquals(expected_document_contents,
                                      actual)
                    source_assertion.apply_with_message(self, source, 'source')

    def test_document_is_not_mandatory_and_not_present(self):
        source_cases = [
            ([
                 '',
             ],
             source_is_at_end),
            ([
                 '    ',
             ],
             source_is_at_end),
            ([
                 '',
                 'line after',
             ],
             source_is_not_at_end(current_line_number=asrt.equals(2),
                                  remaining_part_of_current_line=asrt.equals('line after'))),
        ]
        for source_lines, source_assertion in source_cases:
            with self.subTest(msg=repr((source_lines, source_assertion))):
                source = remaining_source_lines(source_lines)
                actual = sut.parse_as_last_argumentInstrDesc(False, source)
                self.assertIsNone(actual, 'return value from parsing')
                source_assertion.apply_with_message(self, source, 'source')


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingScenarios))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenarios))
    # TODO [instr-desc] Remove when new parser structures are fully integrated
    ret_val.addTest(unittest.makeSuite(TestFailingScenariosOld))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulScenariosOld))
    return ret_val


if __name__ == '__main__':
    unittest.main()
