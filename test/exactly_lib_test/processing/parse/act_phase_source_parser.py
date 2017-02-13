import unittest

from exactly_lib.processing.parse import act_phase_source_parser as sut
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.section_document import model
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib.section_document.parse import LineSequenceSourceFromListOfLines, ListOfLines
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.util import line_source
from exactly_lib_test.test_resources.parse import source3


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestParse2),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParse(unittest.TestCase):  # TODO [instr-desc] remove after new parsing implemented
    def test_parse_single_line_from_single_line_source(self):
        # ARRANGE #
        following_lines = ListOfLines([])
        source = LineSequenceSourceFromListOfLines(following_lines)
        source_builder = line_source.LineSequenceBuilder(source, 1, 'first line')
        # ACT #
        element = sut.PlainSourceActPhaseParser().apply(source_builder)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['first line'])
        self.assertFalse(source.has_next(),
                         'There should be no remaining lines in the source')

    def test_parse_empty_lines_source(self):
        test_cases = [
            ('', []),
            ('  ', []),
            ('', ['']),
            ('  ', ['  ']),
        ]
        for first_src_line, following_src_lines in test_cases:
            with self.subTest(first_line=first_src_line, following_lines=following_src_lines):
                # ARRANGE #
                following_lines = ListOfLines(following_src_lines)
                source = LineSequenceSourceFromListOfLines(following_lines)
                source_builder = line_source.LineSequenceBuilder(source, 1, first_src_line)
                # ACT #
                element = sut.PlainSourceActPhaseParser().apply(source_builder)
                # ASSERT #
                instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
                self.assertEqual(list(instruction.source_code().lines),
                                 [first_src_line] + following_src_lines)
                self.assertFalse(source.has_next(),
                                 'There should be no remaining lines in the source')

    def test_parse_SHOULD_read_all_remaining_lines_if_no_section_header_line_follows(self):
        # ARRANGE #
        following_lines = ListOfLines(['second line',
                                       'third line'])
        source = LineSequenceSourceFromListOfLines(following_lines)
        source_builder = line_source.LineSequenceBuilder(source, 1, 'first line')
        # ACT #
        element = sut.PlainSourceActPhaseParser().apply(source_builder)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['first line',
                          'second line',
                          'third line'])
        self.assertFalse(source.has_next(),
                         'There should be no remaining lines in the source')

    def test_parse_SHOULD_read_all_lines_until_but_not_including_next_section_header_line(self):
        # ARRANGE #
        following_lines = ListOfLines(['second line',
                                       '[section-header]'])
        source = LineSequenceSourceFromListOfLines(following_lines)
        source_builder = line_source.LineSequenceBuilder(source, 1, 'first line')
        # ACT #
        element = sut.PlainSourceActPhaseParser().apply(source_builder)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['first line',
                          'second line'])
        self.assertTrue(source.has_next(),
                        'There should be remaining lines in the source')
        self.assertEqual('[section-header]',
                         source.next_line(),
                         'All following lines should remain in in the source')

    def test_parse_SHOULD_backslash_escape_sequences_at_beginning_of_line(self):
        # ARRANGE #
        following_lines = ListOfLines(['\\\\[second line',
                                       '\\non-escape sequence',
                                       '\\',
                                       '[section-header]'])
        source = LineSequenceSourceFromListOfLines(following_lines)
        source_builder = line_source.LineSequenceBuilder(source, 1, '\\[first line]')
        # ACT #
        element = sut.PlainSourceActPhaseParser().apply(source_builder)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['[first line]',
                          '\\[second line',
                          '\\non-escape sequence',
                          '\\'])
        self.assertTrue(source.has_next(),
                        'There should be remaining lines in the source')
        self.assertEqual('[section-header]',
                         source.next_line(),
                         'All following lines should remain in in the source')

    def test_parse_SHOULD_backslash_escape_sequences_at_beginning_of_line__with_preceding_space(self):
        # ARRANGE #
        following_lines = ListOfLines(['  \\\\[second line',
                                       '   \\non-escape sequence',
                                       '    \\',
                                       '[section-header]'])
        source = LineSequenceSourceFromListOfLines(following_lines)
        source_builder = line_source.LineSequenceBuilder(source, 1, ' \\[first line]')
        # ACT #
        element = sut.PlainSourceActPhaseParser().apply(source_builder)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         [' [first line]',
                          '  \\[second line',
                          '   \\non-escape sequence',
                          '    \\'])
        self.assertTrue(source.has_next(),
                        'There should be remaining lines in the source')
        self.assertEqual('[section-header]',
                         source.next_line(),
                         'All following lines should remain in in the source')

    def _assert_is_instruction_element_with_correct_type_of_instruction(self,
                                                                        element) -> SourceCodeInstruction:
        self.assertIsInstance(element, model.SectionContentElement,
                              'Expecting the parser to have returned a ' + str(model.SectionContentElement))
        assert isinstance(element, model.SectionContentElement)
        instruction = element.instruction
        self.assertIsInstance(instruction, ActPhaseInstruction,
                              'Expecting the instruction to be a ' + str(ActPhaseInstruction))
        assert isinstance(instruction, SourceCodeInstruction)
        return instruction


class TestParse2(unittest.TestCase):
    def test_parse_single_line_from_single_line_source(self):
        # ARRANGE #
        source = source3(['first line'])  # LineSequenceSourceFromListOfLines(following_lines)
        # ACT #
        element = sut.PlainSourceActPhaseParser2().parse(source)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['first line'])
        _assert_source_is_at_end(self, source)

    def test_parse_empty_lines_source(self):
        test_cases = [
            [''],
            ['  '],
            # ['', ''],  # TODO does not work due to peculiar properties of ParseSource
            ['  ', '  '],
        ]
        for source_line in test_cases:
            with self.subTest(source_line=source_line):
                # ARRANGE #
                source = source3(source_line)
                # ACT #
                element = sut.PlainSourceActPhaseParser2().parse(source)
                # ASSERT #
                instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
                self.assertEqual(list(instruction.source_code().lines),
                                 source_line)
                _assert_source_is_at_end(self, source)

    def test_parse_SHOULD_read_all_remaining_lines_if_no_section_header_line_follows(self):
        # ARRANGE #
        source_lines = ['first line',
                        'second line',
                        'third line']
        source = source3(source_lines)
        # ACT #
        element = sut.PlainSourceActPhaseParser2().parse(source)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         source_lines)
        _assert_source_is_at_end(self, source)

    def test_parse_SHOULD_read_all_lines_until_but_not_including_next_section_header_line(self):
        # ARRANGE #
        source_lines = [
            'first line',
            'second line',
            '[section-header]',
        ]
        source = source3(source_lines)
        # ACT #
        element = sut.PlainSourceActPhaseParser2().parse(source)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['first line',
                          'second line'])
        _assert_source_is_not_at_eof_and_has_current_whole_line(self, source, '[section-header]')

    def test_parse_SHOULD_backslash_escape_sequences_at_beginning_of_line(self):
        # ARRANGE #
        source_lines = [
            '\\[first line]',
            '\\\\[second line',
            '\\non-escape sequence',
            '\\',
            '[section-header]',
        ]
        source = source3(source_lines)
        # ACT #
        element = sut.PlainSourceActPhaseParser2().parse(source)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         ['[first line]',
                          '\\[second line',
                          '\\non-escape sequence',
                          '\\'])
        _assert_source_is_not_at_eof_and_has_current_whole_line(self, source, '[section-header]')

    def test_parse_SHOULD_backslash_escape_sequences_at_beginning_of_line__with_preceding_space(self):
        # ARRANGE #
        source_lines = [
            ' \\[first line]',
            '  \\\\[second line',
            '   \\non-escape sequence',
            '    \\',
            '[section-header]',
        ]
        source = source3(source_lines)
        # ACT #
        element = sut.PlainSourceActPhaseParser2().parse(source)
        # ASSERT #
        instruction = self._assert_is_instruction_element_with_correct_type_of_instruction(element)
        self.assertEqual(list(instruction.source_code().lines),
                         [' [first line]',
                          '  \\[second line',
                          '   \\non-escape sequence',
                          '    \\'])
        _assert_source_is_not_at_eof_and_has_current_whole_line(self, source, '[section-header]')

    def _assert_is_instruction_element_with_correct_type_of_instruction(self,
                                                                        element) -> SourceCodeInstruction:
        self.assertIsInstance(element, model.SectionContentElement,
                              'Expecting the parser to have returned a ' + str(model.SectionContentElement))
        assert isinstance(element, model.SectionContentElement)
        instruction = element.instruction
        self.assertIsInstance(instruction, ActPhaseInstruction,
                              'Expecting the instruction to be a ' + str(ActPhaseInstruction))
        assert isinstance(instruction, SourceCodeInstruction)
        return instruction


def _assert_source_is_at_end(put: unittest.TestCase, source: ParseSource):
    put.assertFalse(source.has_current_line,
                    'There should be no remaining lines in the source')
    put.assertTrue(source.is_at_eof,
                   'There should be no remaining data in the source')


def _assert_source_is_not_at_eof_and_has_current_whole_line(put: unittest.TestCase,
                                                            source: ParseSource,
                                                            expected_current_line: str):
    put.assertTrue(source.has_current_line,
                   'There should be remaining lines in the source')
    put.assertFalse(source.is_at_eof,
                    'There should be remaining source')
    put.assertEqual(expected_current_line,
                    source.current_line_text,
                    'Should should have given current line')
    put.assertEqual(expected_current_line,
                    source.remaining_part_of_current_line,
                    'Current line should be identical to remaining-part-of-current-line')
