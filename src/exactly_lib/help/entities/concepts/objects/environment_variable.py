from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity.concepts import ENVIRONMENT_VARIABLE_CONCEPT_INFO
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _EnvironmentVariableConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(ENVIRONMENT_VARIABLE_CONCEPT_INFO)
        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),

            'env_vars__plain': self.name().plural,
            'env_instruction': InstructionName(instruction_names.ENV_VAR_INSTRUCTION_NAME),
            'tcds_concept': formatting.concept_(concepts.TCDS_CONCEPT_INFO),
        })

    def purpose(self) -> DescriptionWithSubSections:
        return DescriptionWithSubSections(
            self.single_line_description(),
            docs.section_contents(
                self._tp.fnap(_INITIAL_PARAGRAPHS),
            ))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            phase_infos.SETUP.instruction_cross_reference_target(instruction_names.ENV_VAR_INSTRUCTION_NAME)
        ]


############################################################
# MENTION
#
# - Which env vars are available
# - Manipulating env vars
# - Scope of change of env vars
############################################################
_INITIAL_PARAGRAPHS = """\
All OS {env_vars__plain}
that are set when {program_name} is started
are available in processes run from a test case.


Environment variables can be manipulated
by the {env_instruction} instruction,
in many phases.


A change of {env_vars__plain} stay in effect for all following instructions and phases.
"""

ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()
