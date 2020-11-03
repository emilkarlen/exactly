from typing import List

from exactly_lib import program_info
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.program import syntax_elements as pgm_syntax_elements
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


def python_interpreter(arguments: List[a.ArgumentUsage]) -> InvokationVariant:
    return invokation_variant_from_args(
        [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Option(pgm_syntax_elements.PYTHON_EXECUTABLE_OPTION_NAME))
        ] +
        arguments,
        _TEXT_PARSER.fnap(_PYTHON_INTERPRETER_DESCRIPTION)
    )


def system_program(arguments: List[a.ArgumentUsage]) -> InvokationVariant:
    return invokation_variant_from_args(
        [
            a.Single(a.Multiplicity.MANDATORY,
                     a.Constant(pgm_syntax_elements.SYSTEM_PROGRAM_TOKEN)
                     ),
            a.Single(a.Multiplicity.MANDATORY,
                     syntax_elements.STRING_SYNTAX_ELEMENT.argument
                     ),
        ] + arguments,
        _TEXT_PARSER.paras(misc_texts.SYSTEM_PROGRAM_DESCRIPTION)
    )


_TEXT_PARSER = TextParser({
    'program_name': formatting.program_name(program_info.PROGRAM_NAME),
    'THE_PYTHON_INTERPRETER': program_info.PYTHON_INTERPRETER_WHICH_CAN_RUN_THIS_PROGRAM,
})

_PYTHON_INTERPRETER_DESCRIPTION = """\
{THE_PYTHON_INTERPRETER}


Since {program_name} is written in Python,
the Python interpreter is guaranteed to be available on the system.
"""
