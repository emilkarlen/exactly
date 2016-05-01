from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.help.utils.render import SectionContentsRenderer


class TestCasePhaseRendererBase(SectionContentsRenderer):
    def __init__(self, test_case_phase_documentation: SectionDocumentation):
        self.test_case_phase_documentation = test_case_phase_documentation


class TestCasePhaseInstructionSetRendererBase(SectionContentsRenderer):
    def __init__(self, instruction_set: SectionInstructionSet):
        self.instruction_set = instruction_set
