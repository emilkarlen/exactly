from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.default.program_modes.test_case.default_instruction_names import ACTOR_INSTRUCTION_NAME
from exactly_lib.help.actors.names_and_cross_references import all_actor_cross_refs, INTERPRETER_ACTOR
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.contents_structure import Name, \
    ConfigurationParameterDocumentation
from exactly_lib.help.cross_reference_id import TestCasePhaseInstructionCrossReference, \
    TestSuiteSectionInstructionCrossReference
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils import suite_section_names
from exactly_lib.help.utils.phase_names import phase_name_dictionary, CONFIGURATION_PHASE_NAME
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs


class _ActorConcept(ConfigurationParameterDocumentation):
    def __init__(self):
        super().__init__(Name('actor', 'actors'))

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'actor_concept': formatting.concept(self.name().singular),
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'actor_option': formatting.cli_option(opt.OPTION_FOR_ACTOR),
            'actor_instruction': formatting.InstructionName(ACTOR_INSTRUCTION_NAME),
            'phase': phase_name_dictionary(),
            'home_directory': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'interpreter_actor': formatting.entity(INTERPRETER_ACTOR.singular_name),
        })
        return DescriptionWithSubSections(parse.text(_SINGLE_LINE_DESCRIPTION),
                                          docs.SectionContents(
                                              parse.fnap(_AFTER_SINGLE_LINE_DESCRIPTION),
                                              [
                                                  docs.section(docs.text('Default actor'),
                                                               parse.fnap(_DEFAULT_DESCRIPTION_REST)),
                                                  docs.section(docs.text('Source code interpreter actor'),
                                                               parse.fnap(_INTERPRETER_ACTOR_DESCRIPTION_REST)),
                                              ]))

    def default_value_str(self) -> str:
        from exactly_lib.help.actors.actor.all_actor_docs import DEFAULT_ACTOR_DOC
        return DEFAULT_ACTOR_DOC.name_and_single_line_description_str()

    def see_also(self) -> list:
        return (all_actor_cross_refs() +
                [
                    HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
                    TestCasePhaseInstructionCrossReference(CONFIGURATION_PHASE_NAME.plain,
                                                           ACTOR_INSTRUCTION_NAME),
                    TestSuiteSectionInstructionCrossReference(suite_section_names.CONFIGURATION_SECTION_NAME.plain,
                                                              ACTOR_INSTRUCTION_NAME),
                ])


ACTOR_CONCEPT = _ActorConcept()

_SINGLE_LINE_DESCRIPTION = """\
Executes tha {phase[act]} phase - interprets the contents of the {phase[act]} phase,
and executes it.
"""

_AFTER_SINGLE_LINE_DESCRIPTION = """\
The {actor_concept} handles {phase[act]} phase - interprets the contents in the test case file,
and executes it.


The {actor_concept} may be specified, via the {actor_instruction} instruction
(both in test cases and test suites),
or the {actor_option} command line option.
"""

_DEFAULT_DESCRIPTION_REST = """\
The default {actor_concept} executes a single command.

It assumes that the {phase[act]} phase consists of a single command line,
where the first element is the path of an executable program.

This path is relative to the {home_directory} (if it is not an absolute path).


The command line uses shell syntax.
"""

_INTERPRETER_ACTOR_DESCRIPTION_REST = """\
The {interpreter_actor} treats the contents of the {phase[act]} phase as source code
to be executed by an interpreter.


The interpreter is an executable program (with optional arguments) that
{program_name} gives a single argument:
the absolute path of a file containing the contents of the {phase[act]} phase.
"""
