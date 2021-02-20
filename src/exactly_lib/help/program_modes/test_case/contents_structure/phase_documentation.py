from typing import List, Sequence, Optional

from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts, directives
from exactly_lib.definitions.section_info import SectionInfo
from exactly_lib.definitions.test_case.phase_infos import TestCasePhaseInfo, TestCasePhaseWithoutInstructionsInfo
from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet, \
    SectionDocumentation
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class PhaseSequenceInfo(tuple):
    def __new__(cls,
                preceding_phase: List[ParagraphItem],
                succeeding_phase: List[ParagraphItem],
                prelude: Sequence[ParagraphItem] = ()):
        return tuple.__new__(cls, (list(prelude), preceding_phase, succeeding_phase))

    @property
    def prelude(self) -> List[ParagraphItem]:
        return self[0]

    @property
    def preceding_phase(self) -> List[ParagraphItem]:
        return self[1]

    @property
    def succeeding_phase(self) -> List[ParagraphItem]:
        return self[2]


class ExecutionEnvironmentInfo(tuple):
    def __new__(cls,
                cwd_at_start_of_phase: List[ParagraphItem],
                prologue: Sequence[ParagraphItem] = (),
                environment_variables_prologue: Sequence[ParagraphItem] = (),
                timeout_prologue: Sequence[ParagraphItem] = (),
                custom_items: Sequence[docs.lists.HeaderContentListItem] = ()):
        return tuple.__new__(cls, (cwd_at_start_of_phase,
                                   list(prologue),
                                   list(environment_variables_prologue),
                                   list(timeout_prologue),
                                   list(custom_items)))

    @property
    def cwd_at_start_of_phase(self) -> List[ParagraphItem]:
        """
        Description of the Present Working Directory, at the start of the phase.
        """
        return self[0]

    @property
    def prologue(self) -> List[ParagraphItem]:
        return self[1]

    @property
    def environment_variables_prologue(self) -> List[ParagraphItem]:
        return self[2]

    @property
    def timeout_prologue(self) -> List[ParagraphItem]:
        return self[3]

    @property
    def custom_items(self) -> List[docs.lists.HeaderContentListItem]:
        return self[4]


class TestCasePhaseDocumentation(SectionDocumentation):
    def __init__(self, section_info: SectionInfo):
        self._section_info = section_info

    @property
    def section_info(self) -> SectionInfo:
        return self._section_info

    def sequence_info(self) -> PhaseSequenceInfo:
        raise NotImplementedError()

    def contents_description(self) -> doc.SectionContents:
        raise NotImplementedError()

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        raise NotImplementedError()


class TestCasePhaseDocumentationForPhaseWithInstructions(TestCasePhaseDocumentation):
    def __init__(self,
                 name: str,
                 instruction_set: Optional[SectionInstructionSet]):
        """
        :param instruction_set: None if this phase does not have instructions.
        """
        super().__init__(TestCasePhaseInfo(name))
        self._instruction_set = instruction_set
        self.__tp = TextParser({
            'directive': concepts.DIRECTIVE_CONCEPT_INFO.name,
            'including': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
        })

    @property
    def has_instructions(self) -> bool:
        return True

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return self._instruction_set

    def contents_description(self) -> doc.SectionContents:
        return docs.section_contents(self.__tp.fnap(_CONTENTS_GENERIC_DESCRIPTION) +
                                     self.instruction_purpose_description())

    def instruction_purpose_description(self) -> List[ParagraphItem]:
        raise NotImplementedError()

    @property
    def see_also_targets(self) -> List[SeeAlsoTarget]:
        ret_val = [
            concepts.INSTRUCTION_CONCEPT_INFO.cross_reference_target,
            concepts.DIRECTIVE_CONCEPT_INFO.cross_reference_target,
        ]
        ret_val += self._see_also_targets_specific
        return ret_val

    @property
    def _see_also_targets_specific(self) -> List[SeeAlsoTarget]:
        return []


class TestCasePhaseDocumentationForPhaseWithoutInstructions(TestCasePhaseDocumentation):
    def __init__(self, name: str):
        super().__init__(TestCasePhaseWithoutInstructionsInfo(name))

    @property
    def has_instructions(self) -> bool:
        return False

    @property
    def instruction_set(self) -> Optional[SectionInstructionSet]:
        return None


_CONTENTS_GENERIC_DESCRIPTION = """\
Consists of zero or more instructions.


Accepts the {including} {directive}.
"""
