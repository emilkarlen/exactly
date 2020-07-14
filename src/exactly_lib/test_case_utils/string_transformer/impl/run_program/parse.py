from typing import Sequence

from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.documentation import texts
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import sdv


def parse(token_parser: TokenParser) -> StringTransformerSdv:
    is_ignore_exit_code = token_parser.consume_optional_option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME)
    program = parse_program.parse_program(token_parser)
    return sdv.sdv(is_ignore_exit_code, program)


class SyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     a.Option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME)),
            syntax_elements.PROGRAM_SYNTAX_ELEMENT.single_mandatory,
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'program': types.PROGRAM_TYPE_INFO.name,
            'The_program_type_must_terminate': texts.THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE,
            'stdin': misc_texts.STDIN,
            'stdout': misc_texts.STDOUT,
            'exit_code': misc_texts.EXIT_CODE,
            'HARD_ERROR': exit_values.EXECUTION__HARD_ERROR.exit_identifier,
            'ignore_exit_code_option': formatting.argument_option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME),
        })
        return tp.fnap(_DESCRIPTION_REST)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.PROGRAM_SYNTAX_ELEMENT.cross_reference_target]


_DESCRIPTION_REST = """\
Runs {program:a}, with input and output via {stdin} and {stdout}.


The result is {HARD_ERROR} if the {exit_code} is non-zero,
unless {ignore_exit_code_option} is given.


{The_program_type_must_terminate}
"""
