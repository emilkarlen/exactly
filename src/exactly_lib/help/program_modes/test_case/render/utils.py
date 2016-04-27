from exactly_lib.help.program_modes.test_case.contents_structure import TestCasePhaseInstructionSet, \
    TestCasePhaseDocumentation
from exactly_lib.help.utils.render import SectionContentsRenderer


class TestCasePhaseRendererBase(SectionContentsRenderer):
    def __init__(self, test_case_phase_documentation: TestCasePhaseDocumentation):
        self.test_case_phase_documentation = test_case_phase_documentation


class TestCasePhaseInstructionSetRendererBase(SectionContentsRenderer):
    def __init__(self, instruction_set: TestCasePhaseInstructionSet):
        self.instruction_set = instruction_set
