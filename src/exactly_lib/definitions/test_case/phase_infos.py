"""New structures for information about phases.
Should replace other structures and values, if found useful.
"""
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseCrossReference, \
    TestCasePhaseInstructionCrossReference
from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.definitions.test_case import phase_names


class TestCasePhaseInfo(SectionInfo):

    @property
    def cross_ref_target(self) -> TestCasePhaseCrossReference:
        return TestCasePhaseCrossReference(self.name.plain)

    def instruction_cross_ref_target(self, instruction_name: str) -> TestCasePhaseInstructionCrossReference:
        return TestCasePhaseInstructionCrossReference(self.name.plain,
                                                      instruction_name)


CONFIGURATION = TestCasePhaseInfo(phase_names.CONFIGURATION)
SETUP = TestCasePhaseInfo(phase_names.SETUP)
ACT = TestCasePhaseInfo(phase_names.ACT)
BEFORE_ASSERT = TestCasePhaseInfo(phase_names.BEFORE_ASSERT)
ASSERT = TestCasePhaseInfo(phase_names.ASSERT)
CLEANUP = TestCasePhaseInfo(phase_names.CLEANUP)
