from typing import List

from exactly_lib.cli.definitions import common_cli_options
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import actors, concepts, syntax_elements
from exactly_lib.definitions.entity import conf_params
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class _ActorConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.ACTOR_CONCEPT_INFO)

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'actor': self.name(),
            'actor_option': formatting.cli_option(common_cli_options.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(instruction_names.ACTOR_INSTRUCTION_NAME),
            'act': phase_infos.ACT.name,
            'default_actor': actors.DEFAULT_ACTOR_SINGLE_LINE_VALUE,
            'null_actor': formatting.entity(actors.NULL_ACTOR.singular_name),
            'actor_conf_param': formatting.conf_param_(conf_params.ACTOR_CONF_PARAM_INFO),
            'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
            'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND),
            'space': misc_texts.WHITESPACE,
        })
        contents = parse.fnap(_AFTER_SINGLE_LINE_DESCRIPTION)
        return DescriptionWithSubSections(self.single_line_description(),
                                          docs.section_contents(contents))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return (
                [
                    phase_infos.ACT.cross_reference_target,
                    conf_params.ACTOR_CONF_PARAM_INFO.cross_reference_target,
                    phase_infos.CONFIGURATION.instruction_cross_reference_target(
                        instruction_names.ACTOR_INSTRUCTION_NAME),
                    PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
                    syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.cross_reference_target,
                ]
                +
                actors.all_actor_cross_refs()
        )


ACTOR_CONCEPT = _ActorConcept()

_AFTER_SINGLE_LINE_DESCRIPTION = """\
The {actor:/q} concept makes it possible to
have different kind of actions executed in the {act} phase.

For example:


 * executable program file
 * source code file
 * source code
 * {shell_command}


{actor:a/u} determines the syntax and semantics of the {act} phase contents.


A test case uses a single {actor}.


Default {actor} is: {default_actor}.


If the contents of {act:syntax} is empty,
or consists of only {space} and comment lines,
then the {null_actor} {actor} is used.


Other {actor:s} are configured via the {actor_conf_param} {conf_param},
or the command line option {actor_option}.
"""
