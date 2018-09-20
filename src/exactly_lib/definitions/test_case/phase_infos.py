"""New structures for information about phases.
Should replace other structures and values, if found useful.
"""
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference, \
    TestCasePhaseInstructionCrossReference
from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.definitions.test_case import phase_names


class TestCasePhaseInfo(SectionInfo):

    @property
    def cross_reference_target(self) -> TestCasePhaseCrossReference:
        return TestCasePhaseCrossReference(self.name.plain)

    def instruction_cross_reference_target(self, instruction_name: str) -> TestCasePhaseInstructionCrossReference:
        return TestCasePhaseInstructionCrossReference(self.name.plain,
                                                      instruction_name)


class TestCasePhaseWithoutInstructionsInfo(TestCasePhaseInfo):
    def instruction_cross_reference_target(self, instruction_name: str) -> TestCasePhaseInstructionCrossReference:
        raise ValueError('The {} phase do not have instructions'.format(self.name.plain))


CONFIGURATION = TestCasePhaseInfo(phase_names.CONFIGURATION.plain)
SETUP = TestCasePhaseInfo(phase_names.SETUP.plain)
ACT = TestCasePhaseWithoutInstructionsInfo(phase_names.ACT.plain)
BEFORE_ASSERT = TestCasePhaseInfo(phase_names.BEFORE_ASSERT.plain)
ASSERT = TestCasePhaseInfo(phase_names.ASSERT.plain)
CLEANUP = TestCasePhaseInfo(phase_names.CLEANUP.plain)
