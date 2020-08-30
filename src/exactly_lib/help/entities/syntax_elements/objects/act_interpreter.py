from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args
from exactly_lib.definitions import misc_texts, formatting, instruction_arguments
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.test_case import actor as help_texts
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation, \
    SyntaxElementDocumentation
from exactly_lib.test_case_utils.parse.shell_syntax import SHELL_KEYWORD
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

_TEXT_PARSER = TextParser({
    'executable_file': formatting.misc_name_with_formatting(misc_texts.EXECUTABLE_FILE),
    'shell_cmd_line': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND_LINE),
    'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
    'shell_syntax_concept': formatting.concept_(concepts.SHELL_SYNTAX_CONCEPT_INFO),
    'external_program': misc_texts.EXTERNAL_PROGRAM,
})

SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD = SHELL_KEYWORD
PROGRAM_ARGUMENT_ARGUMENT = a.Named(help_texts.ARGUMENT)
COMMAND_ARGUMENT = a.Constant(help_texts.COMMAND)


def documentation() -> SyntaxElementDocumentation:
    shell_interpreter_argument = a.Single(a.Multiplicity.MANDATORY,
                                          a.Constant(SHELL_COMMAND_INTERPRETER_ACTOR_KEYWORD))
    command_argument = a.Single(a.Multiplicity.MANDATORY, instruction_arguments.COMMAND_ARGUMENT)
    executable_arg = syntax_elements.PATH_SYNTAX_ELEMENT.single_mandatory
    optional_arguments_arg = a.Single(a.Multiplicity.ZERO_OR_MORE, PROGRAM_ARGUMENT_ARGUMENT)
    invokation_variants = [
        invokation_variant_from_args([executable_arg,
                                      optional_arguments_arg],
                                     _TEXT_PARSER.fnap(_EXECUTABLE_FILE__DESCRIPTION)),
        invokation_variant_from_args([shell_interpreter_argument,
                                      command_argument],
                                     _TEXT_PARSER.fnap(_SHELL_COMMAND__DESCRIPTION)),

    ]
    return syntax_element_documentation(
        None,
        syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT,
        _TEXT_PARSER.fnap(_MAIN__DESCRIPTION),
        (),
        invokation_variants,
        [],
        [
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
            concepts.SHELL_SYNTAX_CONCEPT_INFO.cross_reference_target,
        ],
    )


_MAIN__DESCRIPTION = """\
{external_program:a/u} that interprets a source code file, who's path is given as a command line argument.


When the program is applied, the path of the source code file is added as the last argument.
"""
_EXECUTABLE_FILE__DESCRIPTION = """\
{executable_file:a/u} with arguments.


The {PATH} of the file to interpret is given as an additional last argument.
"""

_SHELL_COMMAND__DESCRIPTION = """\
{shell_cmd_line:a/u}.


The {PATH} of file to interpret (quoted according to {shell_syntax_concept}) is appended
to the end of the command string.
"""
