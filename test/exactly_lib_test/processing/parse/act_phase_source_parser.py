import unittest

from exactly_lib.processing.parse import act_phase_source_parser as sut
from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.section_document import model
from exactly_lib.section_document.parse import LineSequenceSourceFromListOfLines, ListOfLines
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.util import line_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class TestParse(unittest.TestCase):
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
