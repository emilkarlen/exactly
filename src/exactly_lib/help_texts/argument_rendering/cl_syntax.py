from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax

CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()


def cl_syntax_for_args(argument_usages: list) -> str:
    cl = a.CommandLine(argument_usages)
    return cl_syntax(cl)


def cl_syntax(command_line: a.CommandLine) -> str:
    return CL_SYNTAX_RENDERER.as_str(command_line)


def arg_syntax(arg: a.Argument) -> str:
    return ARG_SYNTAX_RENDERER.visit(arg)


def cli_argument_syntax_element_description(argument: a.Argument,
                                            description_rest: list,
                                            invokation_variants: list = None) -> SyntaxElementDescription:
    return SyntaxElementDescription(arg_syntax(argument),
                                    description_rest,
                                    invokation_variants)
