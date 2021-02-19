from typing import List

from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.definitions.test_case.instructions.instruction_names import TIMEOUT_INSTRUCTION_NAME
from exactly_lib.help.entities.concepts.contents_structure import ConceptWDefaultDocumentation
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TimeoutConcept(ConceptWDefaultDocumentation):
    def __init__(self):
        super().__init__(concepts.TIMEOUT_CONCEPT_INFO)
        self._tp = TextParser({
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'os_process': misc_texts.OS_PROCESS_NAME,
            'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
            'timeout_instruction': InstructionName(instruction_names.TIMEOUT_INSTRUCTION_NAME),
        })

    def purpose__before_default(self) -> SectionContents:
        return self._tp.section_contents(WHAT_THE_TIMEOUT_APPLIES_TO)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            phase_infos.SETUP.instruction_cross_reference_target(TIMEOUT_INSTRUCTION_NAME),
        ]


DOCUMENTATION = _TimeoutConcept()

WHAT_THE_TIMEOUT_APPLIES_TO = """\
The timeout is per {os_process}.
It does not apply to the test case as a whole.


It can be changed by the {timeout_instruction} {instruction}.


A change applies to all following {instruction:s} and phases.
"""
