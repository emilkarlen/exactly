from typing import List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import split_arguments_list_string
from exactly_lib.util.cli_syntax.elements import argument as a

MANDATORY_EQ_ARG = a.Single(a.Multiplicity.MANDATORY,
                            a.Named(instruction_arguments.ASSIGNMENT_OPERATOR))


def single_eq_invokation_variants(mandatory_arg: a.Argument) -> list:
    args = [MANDATORY_EQ_ARG,
            a.Single(a.Multiplicity.MANDATORY,
                     mandatory_arg),
            ]
    return [
        InvokationVariant(cl_syntax.cl_syntax_for_args(args)),
    ]


def extract_single_eq_argument_string(rest_of_line: str) -> str:
    arguments = split_arguments_list_string(rest_of_line)
    if len(arguments) != 2:
        msg = 'Invalid number of arguments, expected 2, found {}'.format(str(len(arguments)))
        raise SingleInstructionInvalidArgumentException(msg)
    if arguments[0] != instruction_arguments.ASSIGNMENT_OPERATOR:
        raise SingleInstructionInvalidArgumentException('Missing =')
    return arguments[1]


def extract_mandatory_arguments_after_eq(rest_of_line: str) -> List[str]:
    arguments = split_arguments_list_string(rest_of_line)
    if not arguments:
        raise SingleInstructionInvalidArgumentException('Missing arguments')
    if arguments[0] != instruction_arguments.ASSIGNMENT_OPERATOR:
        raise SingleInstructionInvalidArgumentException('Missing ' + instruction_arguments.ASSIGNMENT_OPERATOR)
    del arguments[0]
    if not arguments:
        raise SingleInstructionInvalidArgumentException('Missing arguments')
    return arguments
