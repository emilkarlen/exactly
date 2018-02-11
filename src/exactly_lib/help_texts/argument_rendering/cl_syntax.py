from typing import Sequence

from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.render import cli_program_syntax

CL_SYNTAX_RENDERER = cli_program_syntax.CommandLineSyntaxRenderer()

ARG_SYNTAX_RENDERER = cli_program_syntax.ArgumentInArgumentDescriptionRenderer()


def cl_syntax_for_args(argument_usages: Sequence[a.ArgumentUsage]) -> str:
    cl = a.CommandLine(argument_usages)
    return cl_syntax(cl)


def cl_syntax(command_line: a.CommandLine) -> str:
    return CL_SYNTAX_RENDERER.as_str(command_line)


def arg_syntax(arg: a.Argument) -> str:
    return ARG_SYNTAX_RENDERER.visit(arg)
