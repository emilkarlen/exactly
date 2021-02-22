from typing import Sequence

from exactly_lib.definitions import misc_texts, matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.impls import texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import sdv


def parse(token_parser: TokenParser) -> StringTransformerSdv:
    is_ignore_exit_code = token_parser.consume_optional_option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME)
    program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)
    return sdv.sdv(is_ignore_exit_code, program)


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
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
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'stdin': misc_texts.STDIN,
            'stdout': misc_texts.STDOUT,
            'model': matcher_model.TEXT_MODEL,
        })
        return tp.fnap(_DESCRIPTION_REST) + texts.run_outcome__with_ignored_exit_code_option()

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.PROGRAM_SYNTAX_ELEMENT.cross_reference_target]


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)

_DESCRIPTION_REST = """\
Runs {program:a}, with input and output via {stdin} and {stdout}.


If {PROGRAM} defines {stdin}, then the {model} to transform is appended to that {stdin}.
"""
