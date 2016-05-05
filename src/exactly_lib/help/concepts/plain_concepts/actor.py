from exactly_lib import program_info
from exactly_lib.cli.cli_environment.program_modes.test_case import command_line_options as opt
from exactly_lib.help.concepts.configuration_parameters.home_directory import HOME_DIRECTORY_CONFIGURATION_PARAMETER
from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.utils import formatting
from exactly_lib.help.utils.description import DescriptionWithSubSections
from exactly_lib.help.utils.phase_names import phase_name_dictionary
from exactly_lib.help.utils.textformat_parse import TextParser
from exactly_lib.util.textformat.structure import structures as docs


class _ActorConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('actor', 'actors'))

    def purpose(self) -> DescriptionWithSubSections:
        parse = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'actor_option': formatting.cli_option(opt.OPTION_FOR_ACTOR__LONG),
            'phase': phase_name_dictionary(),
            'home_directory': formatting.concept(HOME_DIRECTORY_CONFIGURATION_PARAMETER.name().singular),
            'interpreter_actor': formatting.term(opt.INTERPRETER_ACTOR_TERM),
        })
        return DescriptionWithSubSections(docs.text(parse.format(_SINGLE_LINE_DESCRIPTION)),
                                          docs.SectionContents(
                                              [],
                                              [
                                                  docs.section(docs.text('Default actor'),
                                                               parse.fnap(_DEFAULT_DESCRIPTION_REST)),
                                                  docs.section(docs.text('Source code interpreter actor'),
                                                               parse.fnap(_INTERPRETER_ACTOR_DESCRIPTION_REST)),
                                              ]))

    def see_also(self) -> list:
        return [
            HOME_DIRECTORY_CONFIGURATION_PARAMETER.cross_reference_target(),
        ]


ACTOR_CONCEPT = _ActorConcept()

_SINGLE_LINE_DESCRIPTION = """\
Responsible for reading the contents of the {phase[act]} phase,
and executing it as part of the execution of the test case.
"""

_DEFAULT_DESCRIPTION_REST = """\
By default, the {phase[act]} phase must consist of a single command line.


The command line uses shell syntax.


The first element of the command line must be the path of an executable program.

The path is relative to the {home_directory}.
"""

_INTERPRETER_ACTOR_DESCRIPTION_REST = """\
The {interpreter_actor} treats the contents of the {phase[act]} phase as source code
to be executed by an interpreter.


The interpreter is an executable program (with optional arguments) that
{program_name} gives a single argument:
the absolute path of a file containing the contents of the {phase[act]} phase.


The {interpreter_actor} is specified, e.g., via the {actor_option} option.
"""
