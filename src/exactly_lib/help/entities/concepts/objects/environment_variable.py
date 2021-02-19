from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_infos, phase_names
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptWDefaultDocumentation
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _EnvironmentVariableConcept(ConceptWDefaultDocumentation):
    def __init__(self):
        super().__init__(concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO)

    def purpose__before_default(self) -> SectionContents:
        description = common_description()
        description += _TP.fnap(_DESCRIPTION_TAIL)
        return SectionContents(description)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.ENV_VAR_INSTRUCTION_NAME)
        ]


def common_description() -> List[ParagraphItem]:
    return _TP.fnap(_DESCRIPTION__COMMON)


############################################################
# MENTION
#
# - Two sets of env vars
# - Manipulating env vars
# - Scope of change of env vars
############################################################
_DESCRIPTION__COMMON = """\
{program_name} maintains two sets of {env_var:s}:


  * variables of the {atc:/q} executed by the {act_phase:emphasis} phase

  * variables of {os_process:s} executed from phases other than the {act_phase:emphasis} phase


{env_var:s/u} can be manipulated
by the {env_instruction} {instruction}.
"""

_DESCRIPTION_TAIL = """\
A change of {env_var:s} stay in effect for all following {instruction:s} and phases.
"""

ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()

_TP = TextParser({
    'program_name': formatting.program_name(program_info.PROGRAM_NAME),
    'process': misc_texts.OS_PROCESS_NAME,
    'env_var': concepts.ENVIRONMENT_VARIABLE_CONCEPT_INFO.name,
    'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
    'atc': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
    'act_phase': phase_names.ACT,
    'os_process': misc_texts.OS_PROCESS_NAME,
    'env_instruction': InstructionName(instruction_names.ENV_VAR_INSTRUCTION_NAME),
})
