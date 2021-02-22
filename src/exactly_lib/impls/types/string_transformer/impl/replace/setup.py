from typing import Sequence

from exactly_lib.common.help import headers
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args
from exactly_lib.definitions import formatting, misc_texts, matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity import types
from exactly_lib.impls import texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.impls.types.parse import options as _parse_options
from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer.impl.replace import impl as _impl
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class ParserOfReplace(ParserFromTokens[StringTransformerSdv]):
    def __init__(self):
        self._parser_of_lines_selection = _parse_options.OptionalOptionWMandatoryArgumentParser(
            names.LINES_SELECTION_OPTION_NAME,
            parse_line_matcher.parsers(must_be_on_current_line=False).simple,
        )
        self._parser_of_regex = parse_regex.ParserOfRegex()
        self._parser_of_replacement = parse_string.StringFromTokensParser(_PARSE_REPLACEMENT_CONFIGURATION)

    def parse(self, token_parser: TokenParser) -> StringTransformerSdv:
        token_parser.require_has_valid_head_token(_REGEX_ARGUMENT.name)
        mb_line_matcher = self._parser_of_lines_selection.parse_from_token_parser(token_parser)
        preserve_new_lines = token_parser.consume_optional_option(names.PRESERVE_NEW_LINES_OPTION_NAME)
        regex_sdv = self._parser_of_regex.parse(token_parser)
        replacement = self._parser_of_replacement.parse(token_parser)

        return _impl.Sdv(mb_line_matcher,
                         preserve_new_lines,
                         regex_sdv,
                         replacement)


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    LINES_SELECTOR = a.Named('LINES-SELECTION')

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     self.LINES_SELECTOR),
            a.Single(a.Multiplicity.OPTIONAL,
                     names.PRESERVE_NEW_LINES_OPTION),
            a.Single(a.Multiplicity.MANDATORY,
                     _REGEX_ARGUMENT),
            a.Single(a.Multiplicity.MANDATORY,
                     _REPLACEMENT_ARGUMENT),
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_DESCRIPTION)

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return [
            self._lines_selection_syntax_elements()
        ]

    def _lines_selection_syntax_elements(self) -> SyntaxElementDescription:
        description = _TEXT_PARSER.fnap(_DESCRIPTION__LINES_SELECTION)
        description += texts.type_expression_has_syntax_of_primitive([
            names.LINES_SELECTION_OPTION.argument,
        ])
        return SyntaxElementDescription(
            self.LINES_SELECTOR.name,
            (),
            [
                invokation_variant_from_args(
                    [a.Single(a.Multiplicity.MANDATORY, names.LINES_SELECTION_OPTION)],
                )
            ],
            description,
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target]


_REGEX_ARGUMENT = syntax_elements.REGEX_SYNTAX_ELEMENT.argument

_REPLACEMENT_ARGUMENT = a.Named(types.STRING_TYPE_INFO.syntax_element_name)
_MISSING_REPLACEMENT_ARGUMENT_ERR_MSG = 'Missing ' + _REPLACEMENT_ARGUMENT.name

_PARSE_REPLACEMENT_CONFIGURATION = parse_string.Configuration('REPLACEMENT')

_TEXT_PARSER = TextParser({
    'preserve_new_lines_option': formatting.argument_option(names.PRESERVE_NEW_LINES_OPTION_NAME),
    '_REG_EX_': _REGEX_ARGUMENT.name,
    '_STRING_': _REPLACEMENT_ARGUMENT.name,
    'plain_string': misc_texts.PLAIN_STRING,
    'LINES_SELECTOR_MATCHER': names.LINES_SELECTION_OPTION.argument,
    'line_matcher_model': matcher_model.LINE_MATCHER_MODEL,
    'Note': headers.NOTE_LINE_HEADER,
    'NL': formatting.string_constant('\\n'),
    'LINES_ARE_SEPARATED_BY_NEW_LINE': misc_texts.LINES_ARE_SEPARATED_BY_NEW_LINE,
})

_DESCRIPTION = """\
Replaces every {plain_string} matching {_REG_EX_} (on a single line) with {_STRING_}.


Backslash escapes in {_STRING_} are processed.
That is, \\n is converted to a single newline character, \\r is converted to a carriage return, and so forth.


Unknown escapes such as \\& are left alone.


Back-references, such as \\6, are replaced with the sub{plain_string} matched by group 6 in {_REG_EX_}.


Every line ends with {NL},
except the last line, which may or may not end with {NL}.

If {preserve_new_lines_option} is given,
this {NL} is excluded from the replacement.


{Note}
{LINES_ARE_SEPARATED_BY_NEW_LINE}
"""

_DESCRIPTION__LINES_SELECTION = """\
Limits replacement to {line_matcher_model:s} matching {LINES_SELECTOR_MATCHER}.
"""
