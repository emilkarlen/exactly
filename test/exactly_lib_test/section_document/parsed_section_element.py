import unittest

from exactly_lib.section_document import parsed_section_element as sut
from exactly_lib.section_document.model import InstructionInfo, Instruction, ElementType
from exactly_lib.util import line_source


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(ParsedSectionElementVisitor)


class ArgumentRecordingArgumentVisitor(sut.ParsedSectionElementVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_instruction_element(self, instruction: sut.ParsedInstruction):
        self.visited_classes.append(sut.ParsedInstruction)
        return instruction

    def visit_non_instruction_element(self, non_instruction: sut.ParsedNonInstructionElement):
        self.visited_classes.append(sut.ParsedNonInstructionElement)
        return non_instruction

    def visit_file_inclusion_directive(self, file_inclusion: sut.ParsedFileInclusionDirective):
        self.visited_classes.append(sut.ParsedFileInclusionDirective)
        return file_inclusion


class ParsedSectionElementVisitor(unittest.TestCase):
    def test_instruction_element(self):
        self._check(sut.ParsedInstruction(LINE_SEQUENCE, INSTRUCTION_INFO), sut.ParsedInstruction)

    def test_non_instruction_element(self):
        self._check(sut.ParsedNonInstructionElement(LINE_SEQUENCE, ElementType.COMMENT),
                    sut.ParsedNonInstructionElement)

    def test_file_inclusion_directive(self):
        self._check(sut.ParsedFileInclusionDirective(LINE_SEQUENCE, []),
                    sut.ParsedFileInclusionDirective)

    def test_visit_SHOULD_raise_TypeError_WHEN_argument_is_not_a_sub_class_of_argument(self):
        visitor = ArgumentRecordingArgumentVisitor()
        with self.assertRaises(TypeError):
            visitor.visit(UnknownParsedSectionElementSubClass(LINE_SEQUENCE))

    def _check(self, x: sut.ParsedSectionElement, expected_class):
        # ARRANGE #
        visitor = ArgumentRecordingArgumentVisitor()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertListEqual([expected_class],
                             visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'Visitor should return the return-value of the visited method')


class UnknownParsedSectionElementSubClass(sut.ParsedSectionElement):
    def __init__(self, source: line_source.LineSequence):
        super().__init__(source)


LINE_SEQUENCE = line_source.LineSequence(1, ('line text',))

INSTRUCTION_INFO = InstructionInfo(Instruction(), 'description')
