from exactly_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpRendererBase
from exactly_lib.help.utils.render import RenderingEnvironment
from exactly_lib.help.program_modes.common.renderers import instruction_set_list
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import text


class InstructionSetPerPhaseRenderer(TestCaseHelpRendererBase):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        sections = []
        for test_case_phase_help in self.test_case_help.phase_helps_in_order_of_execution:
            if test_case_phase_help.has_instructions:
                instruction_list = instruction_set_list(test_case_phase_help.instruction_set)
                sections.append(doc.Section(text(test_case_phase_help.name.syntax),
                                            doc.SectionContents([instruction_list], [])))
        return doc.SectionContents([], sections)
