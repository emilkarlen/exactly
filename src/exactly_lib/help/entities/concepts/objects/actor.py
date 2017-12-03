from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help_texts.entity import actors
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.help_texts.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import CONFIGURATION_PHASE_NAME, \
    PHASE_NAME_DICTIONARY
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _ActorConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(ACTOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'actor_concept': formatting.concept(self.singular_name()),
            'actor_option': formatting.cli_option(opt.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'phase': PHASE_NAME_DICTIONARY,
        })
        contents = parse.fnap(_AFTER_SINGLE_LINE_DESCRIPTION) + parse.fnap(HOW_TO_SPECIFY_ACTOR)
        return DescriptionWithSubSections(self.single_line_description(),
                                          docs.section_contents(contents))

    def see_also_targets(self) -> list:
        return (
            [
                conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
                TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                       ACTOR_INSTRUCTION_NAME),
                TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                          ACTOR_INSTRUCTION_NAME),
            ]
            +
            actors.all_actor_cross_refs()
        )


ACTOR_CONCEPT = _ActorConcept()

_AFTER_SINGLE_LINE_DESCRIPTION = """\
The {actor_concept} handles {phase[act]} phase - interprets the contents in the test case file,
and executes it.
"""

HOW_TO_SPECIFY_ACTOR = """\
The {actor_concept} may be specified, via the {actor_instruction} instruction
(both in test cases and test suites),
or the {actor_option} command line option.
"""
