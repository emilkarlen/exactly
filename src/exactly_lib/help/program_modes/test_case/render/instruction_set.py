from exactly_lib.help.program_modes.common.renderers import SectionInstructionSetConstructor
from exactly_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpConstructorBase
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.structures import text


class InstructionSetPerPhaseRenderer(TestCaseHelpConstructorBase):
    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        sections = []
        for test_case_phase_help in self.test_case_help.phase_helps_in_order_of_execution:
            if test_case_phase_help.has_instructions:
                renderer = SectionInstructionSetConstructor(
                    test_case_phase_help.instruction_set,
                    instruction_group_by=test_case_phase_help.instruction_group_by)
                sections.append(docs.Section(text(test_case_phase_help.name.syntax),
                                             renderer.apply(environment)))
        return doc.SectionContents([], sections)
