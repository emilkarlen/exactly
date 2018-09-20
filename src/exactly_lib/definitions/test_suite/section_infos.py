"""New structures for information about sections.
Should replace other structures and values, if found useful.
"""
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestSuiteSectionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.definitions.test_suite import section_names


class TestSuiteSectionInfo(SectionInfo):

    @property
    def cross_reference_target(self) -> TestSuiteSectionCrossReference:
        return TestSuiteSectionCrossReference(self.name.plain)

    def instruction_cross_reference_target(self, instruction_name: str) -> TestSuiteSectionInstructionCrossReference:
        return TestSuiteSectionInstructionCrossReference(self.name.plain,
                                                         instruction_name)


class TestSuiteSectionWithoutInstructionsInfo(TestSuiteSectionInfo):
    def instruction_cross_reference_target(self, instruction_name: str) -> TestSuiteSectionInstructionCrossReference:
        raise ValueError('The {} section do not have instructions'.format(self.name.plain))


CONFIGURATION = TestSuiteSectionInfo(section_names.CONFIGURATION)
CASES = TestSuiteSectionWithoutInstructionsInfo(section_names.CASES)
SUITES = TestSuiteSectionWithoutInstructionsInfo(section_names.SUITES)

CASE__SETUP = TestSuiteSectionInfo(section_names.CASE__SETUP)
CASE__ACT = TestSuiteSectionInfo(section_names.CASE__ACT)
CASE__BEFORE_ASSERT = TestSuiteSectionInfo(section_names.CASE__BEFORE_ASSERT)
CASE__ASSERT = TestSuiteSectionInfo(section_names.CASE__ASSERT)
CASE__CLEANUP = TestSuiteSectionInfo(section_names.CASE__CLEANUP)
