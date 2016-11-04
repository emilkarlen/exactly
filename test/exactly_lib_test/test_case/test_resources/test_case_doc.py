from exactly_lib.section_document import model as doc
from exactly_lib.test_case import test_case_doc
from exactly_lib.util import line_source


class TestCaseWithOnlyInstructionElementsBuilder:
    def __init__(self,
                 configuration_phase: list = None,
                 setup_phase: list = None,
                 act_phase: list = None,
                 before_assert_phase: list = None,
                 assert_phase: list = None,
                 cleanup_phase: list = None):
        self.configuration_phase = self._list_of(configuration_phase)
        self.setup_phase = self._list_of(setup_phase)
        self.act_phase = self._list_of(act_phase)
        self.before_assert_phase = self._list_of(before_assert_phase)
        self.assert_phase = self._list_of(assert_phase)
        self.cleanup_phase = self._list_of(cleanup_phase)

    @staticmethod
    def _list_of(list_or_none) -> list:
        return [] if list_or_none is None else list_or_none

    def build(self) -> test_case_doc.TestCase:
        element_generator = InstructionElementGenerator()
        return test_case_doc.TestCase(element_generator.section_contents(self.configuration_phase),
                                      element_generator.section_contents(self.setup_phase),
                                      element_generator.section_contents(self.act_phase),
                                      element_generator.section_contents(self.before_assert_phase),
                                      element_generator.section_contents(self.assert_phase),
                                      element_generator.section_contents(self.cleanup_phase),
                                      )


class InstructionElementGenerator:
    def __init__(self):
        self._current_line = 1

    def instruction_element(self, instruction) -> doc.SectionContentElement:
        line_no = self._current_line
        self._current_line += 1
        source = line_source.LineSequence(line_no, ('Line ' + str(line_no),))
        return doc.new_instruction_e(source, instruction)

    def instruction_elements(self, instructions) -> tuple:
        return tuple(map(self.instruction_element, instructions))

    def section_contents(self, instructions) -> doc.SectionContents:
        return doc.SectionContents(self.instruction_elements(instructions))
