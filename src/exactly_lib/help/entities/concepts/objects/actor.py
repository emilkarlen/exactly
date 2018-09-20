from typing import List

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.definitions.entity import actors, concepts
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _ActorConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(ACTOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'actor_concept': formatting.concept(self.singular_name()),
            'actor_option': formatting.cli_option(common_cli_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(instruction_names.ACTOR_INSTRUCTION_NAME),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
        })
        contents = parse.fnap(_AFTER_SINGLE_LINE_DESCRIPTION) + parse.fnap(HOW_TO_SPECIFY_ACTOR)
        return DescriptionWithSubSections(self.single_line_description(),
                                          docs.section_contents(contents))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return (
                [
                    phase_infos.ACT.cross_reference_target,
                    conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
                    TestCasePhaseInstructionCrossReference(phase_names.CONFIGURATION.plain,
                                                           instruction_names.ACTOR_INSTRUCTION_NAME),
                ]
                +
                actors.all_actor_cross_refs()
        )


ACTOR_CONCEPT = _ActorConcept()

_AFTER_SINGLE_LINE_DESCRIPTION = """\
The {actor_concept} handles {phase[act]} phase -
interprets the contents of the {phase[act]} phase in the test case file,
and executes it as the {action_to_check}.


The {action_to_check} is executed in it's own process.
"""

HOW_TO_SPECIFY_ACTOR = """\
The {actor_concept} may be specified, via the {actor_instruction} instruction
in test cases,
or the {actor_option} command line option.
"""
