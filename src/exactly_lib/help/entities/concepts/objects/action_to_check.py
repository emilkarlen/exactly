from typing import List

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.definitions.test_case.phase_names import PHASE_NAME_DICTIONARY
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _ActionToCheckConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.ACTION_TO_CHECK_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parser = TextParser({
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'actor_concept': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'actor_option': formatting.cli_option(common_cli_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'phase': PHASE_NAME_DICTIONARY,
        })
        return DescriptionWithSubSections(concepts.ACTION_TO_CHECK_CONCEPT_INFO.single_line_description,
                                          docs.section_contents(parser.fnap(_DESCRIPTION)))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return (
            [
                phase_infos.ACT.cross_reference_target,
                concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
            ]
        )


ACTOR_CONCEPT = _ActionToCheckConcept()

_DESCRIPTION = """\
The {action_to_check} is specified jointly by
the configured {actor_concept}
and the contents of the {phase[act]} phase.


The {actor_concept} is responsible for interpreting the contents
of the {phase[act]}, and executing it.


It is executed in it's own process.


Depending on which {actor_concept} is configured,
the {action_to_check} may be, for example:


 * executable program (together with arguments)
 * source file
 * source code
 * shell command
"""
