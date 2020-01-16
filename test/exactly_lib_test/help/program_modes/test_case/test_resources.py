from typing import Optional, List

from exactly_lib.definitions.test_case.phase_infos import TestCasePhaseWithoutInstructionsInfo
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_case.contents_structure.phase_documentation import TestCasePhaseDocumentation, \
    PhaseSequenceInfo, ExecutionEnvironmentInfo
from exactly_lib.help.program_modes.test_case.contents_structure.test_case_help import TestCaseHelp
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib_test.help.test_resources import section_instruction_set


def test_case_help_with_production_phases() -> TestCaseHelp:
    return TestCaseHelp([
        _phase_doc(phase_identifier.CONFIGURATION.identifier, []),
        _phase_doc(phase_identifier.SETUP.identifier, []),
        _phase_doc(phase_identifier.ACT.identifier, []),
        _phase_doc(phase_identifier.BEFORE_ASSERT.identifier, []),
        _phase_doc(phase_identifier.ASSERT.identifier, []),
        _phase_doc(phase_identifier.CLEANUP.identifier, []),
    ])


def _phase_doc(phase_name: str,
               instruction_names: List[str]) -> TestCasePhaseDocumentation:
    instruction_set = section_instruction_set(phase_name, instruction_names)
    return _SectionDocumentationForTestCasePhaseWithInstructionsTestImpl(phase_name,
                                                                         instruction_set)


class _SectionDocumentationForTestCasePhaseWithInstructionsTestImpl(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(TestCasePhaseWithoutInstructionsInfo(name))
        self._instruction_set = instruction_set

    def purpose(self) -> Description:
        return Description(docs.text('Single line purpose for phase ' + self.name.syntax),
                           [docs.para('Rest of purpose for phase ' + self.name.syntax)])

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo(docs.paras('preceding phase'),
                                 docs.paras('succeeding phase'),
                                 docs.paras('prelude'))

    def contents_description(self) -> doc.SectionContents:
        return docs.section_contents(
            docs.paras('initial paragraphs')
        )

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(
            docs.paras('ced_at_start_of_phase'),
            tuple(docs.paras('prologue')),
        )

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return self._instruction_set
