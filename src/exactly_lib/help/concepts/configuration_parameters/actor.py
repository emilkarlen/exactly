from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.common.help.cross_reference_id import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help.actors.names_and_cross_references import all_actor_cross_refs, SOURCE_INTERPRETER_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help.concepts.names_and_cross_references import ACTOR_CONCEPT_INFO
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions.instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help_texts.test_case.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.help_texts.test_suite import formatted_section_names
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class _ActorConcept(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(ACTOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'actor_concept': formatting.concept(self.name().singular),
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'actor_option': formatting.cli_option(opt.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'phase': phase_name_dictionary(),
            'home_directory': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'interpreter_actor': formatting.entity(SOURCE_INTERPRETER_ACTOR.singular_name),
        })
        contents = parse.fnap(_AFTER_SINGLE_LINE_DESCRIPTION) + parse.fnap(HOW_TO_SPECIFY_ACTOR)
        return DescriptionWithSubSections(self.single_line_description(),
                                          docs.section_contents(contents))

    def default_value_str(self) -> str:
        from exactly_lib.help.actors.actor.all_actor_docs import DEFAULT_ACTOR_DOC
        return (formatting.entity(DEFAULT_ACTOR_DOC.singular_name()) +
                ' - ' +
                DEFAULT_ACTOR_DOC.single_line_description_str())

    def _see_also_cross_refs(self) -> list:
        return (all_actor_cross_refs() +
                [
                    TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                           ACTOR_INSTRUCTION_NAME),
                    TestSuiteSectionInstructionCrossReference(formatted_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                              ACTOR_INSTRUCTION_NAME),
                ])


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
