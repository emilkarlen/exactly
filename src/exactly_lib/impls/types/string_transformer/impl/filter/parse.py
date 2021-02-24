from typing import Sequence

from exactly_lib.common.help import headers
from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_string
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions import doc_format
from exactly_lib.definitions import formatting
from exactly_lib.definitions.argument_rendering import cl_syntax
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher as line_matcher_primitives
from exactly_lib.definitions.test_case.instructions import define_symbol as help_texts
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.impls.types.line_matcher.impl.contents import parse as parse_line_matcher_contents
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.impls.types.string_matcher import matcher_options as sm_matcher_options
from exactly_lib.impls.types.string_matcher.parse import matches as parse_sm_matches
from exactly_lib.section_document.element_parsers import token_stream_parsing as parsing
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    is_string__all_indirect_refs_are_strings
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.matcher import line_matcher as line_matcher_type
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import line_matcher
from .line_nums import resolvers as line_nums_resolvers
from ... import names


class GrepShortcutParser(ParserFromTokens[StringTransformerSdv]):
    def __init__(self, name_of_primitive: str):
        self._name__line_matcher = _name__line_matcher(name_of_primitive)

    def parse(self, token_parser: TokenParser) -> StringTransformerSdv:
        string_matcher = parse_sm_matches.parse(token_parser)
        line_matcher_ = parse_line_matcher_contents.sdv(string_matcher)
        return line_matcher.sdv(self._name__line_matcher, line_matcher_)


class Parser(ParserFromTokens[StringTransformerSdv]):
    def __init__(self, name_of_primitive: str):
        self._name__line_nums = ' '.join((
            name_of_primitive,
            cl_syntax.cl_syntax_for_args(_ARGUMENTS__LINE_NUMS),
        ))

        self._name__line_matcher = _name__line_matcher(name_of_primitive)

        self._range_expr_parser = parse_string.StringFromTokensParser(
            parse_string.Configuration(names.RANGE_EXPR_SED_NAME,
                                       _RANGE_EXPR_REFERENCE_RESTRICTIONS)
        )

        self._line_matcher_parser = parse_line_matcher.parsers(False).simple

        choices = [
            parsing.TokenSyntaxSetup(
                token_matchers.is_option(names.LINE_NUMBERS_FILTER_OPTION.name),
                self._parse_line_nums_variant,
            ),
        ]

        self._choice_parser = parsing.ParserOfOptionalChoiceWithDefault(
            choices,
            self._parse_line_matcher_variant,
        )

    def parse(self, token_parser: TokenParser) -> StringTransformerSdv:
        return self._choice_parser.parse(token_parser)

    def _parse_line_matcher_variant(self, token_parser: TokenParser) -> StringTransformerSdv:
        line_matcher_ = self._line_matcher_parser.parse_from_token_parser(token_parser)
        return line_matcher.sdv(self._name__line_matcher, line_matcher_)

    def _parse_line_nums_variant(self, token_parser: TokenParser) -> StringTransformerSdv:
        range_expr_list = [self._range_expr_parser.parse(token_parser)]
        while not token_parser.is_at_eol:
            range_expr_list.append(self._range_expr_parser.parse(token_parser))

        return line_nums_resolvers.sdv(self._name__line_nums, range_expr_list)


_ARGUMENTS__LINE_NUMS = [a.Single(a.Multiplicity.MANDATORY, names.LINE_NUMBERS_FILTER_OPTION),
                         a.Single(a.Multiplicity.ONE_OR_MORE, a.Named(names.RANGE_EXPR_SED_NAME))]

_MATCHER_ARGUMENT = a.Named('MATCHER')

_RANGE_LIMIT_SEPARATOR = ':'

_RANGE_EXPR_REFERENCE_RESTRICTIONS = is_string__all_indirect_refs_are_strings(
    text_docs.single_pre_formatted_line_object(
        str_constructor.FormatMap(
            'A {RANGE} must be made up of just {string_type} values.',
            {
                'RANGE': names.RANGE_EXPR_SED_NAME,
                'string_type': help_texts.ANY_TYPE_INFO_DICT[ValueType.STRING].identifier
            }
        )
    )
)


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self):
        self._tp = TextParser({
            'MATCHER': _MATCHER_ARGUMENT.name,
            '_LINE_MATCHER_': syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name,
            'FIRST_LINE_NUMBER': line_matcher_type.FIRST_LINE_NUMBER,
            'FIRST_LINE_NUMBER_DESCRIPTION': line_matcher_type.FIRST_LINE_NUMBER_DESCRIPTION,
            'LINE_SEPARATOR_DESCRIPTION': line_matcher_type.LINE_SEPARATOR_DESCRIPTION,
            'RANGE': names.RANGE_EXPR_SED_NAME,
            'INT': syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name,
            'RANGE_LIMIT_SEPARATOR': formatting.string_constant(_RANGE_LIMIT_SEPARATOR),
            'Note': headers.NOTE_LINE_HEADER,
        })

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.MANDATORY, _MATCHER_ARGUMENT),
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return (
                self._tp.fnap(_DESCRIPTION__MAIN) +
                [self._variants_table()] +
                self._tp.fnap(_DESCRIPTION__MAIN__EPILOGUE)
        )

    def _variants_table(self) -> ParagraphItem:
        return docs.simple_list_with_space_between_elements_and_content(
            [
                self._item([syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.single_mandatory],
                           _DESCRIPTION__LINE_MATCHER),
                self._item(_ARGUMENTS__LINE_NUMS,
                           _DESCRIPTION__LINE_NUMS),
            ],
            lists.ListType.VARIABLE_LIST,
        )

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return [self._range_expr_sed()]

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [
            syntax_elements.INTEGER_SYNTAX_ELEMENT.cross_reference_target,
            syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _range_expr_sed(self) -> SyntaxElementDescription:
        int_val = syntax_elements.INTEGER_SYNTAX_ELEMENT.singular_name
        return SyntaxElementDescription(
            names.RANGE_EXPR_SED_NAME,
            self._tp.fnap(_RANGE_EXPR__DESCRIPTION),
            [
                invokation_variant_from_string(
                    int_val,
                    self._tp.fnap(_RANGE_EXPR__DESCRIPTION__INT)
                ),
                invokation_variant_from_string(
                    _RANGE_LIMIT_SEPARATOR + int_val,
                    self._tp.fnap(_RANGE_EXPR__DESCRIPTION__UPPER)
                ),
                invokation_variant_from_string(
                    int_val + _RANGE_LIMIT_SEPARATOR,
                    self._tp.fnap(_RANGE_EXPR__DESCRIPTION__LOWER)
                ),
                invokation_variant_from_string(
                    _RANGE_LIMIT_SEPARATOR.join((int_val, int_val)),
                    self._tp.fnap(_RANGE_EXPR__DESCRIPTION__LOWER_UPPER)
                ),
            ],
            after_invokation_variants=self._tp.fnap(_RANGE_EXPR__PROLOGUE)
        )

    def _item(self,
              arguments: Sequence[a.ArgumentUsage],
              description_template: str,
              ) -> lists.HeaderContentListItem:
        return docs.list_item(
            doc_format.syntax_text(cl_syntax.cl_syntax_for_args(arguments)),
            self._tp.fnap(description_template)
        )


class GrepShortcutSyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, name_of_aliased: str):
        target_components = (name_of_aliased,
                             line_matcher_primitives.CONTENTS_MATCHER_NAME,
                             sm_matcher_options.MATCHES_ARGUMENT)
        self._tp = TextParser({
            'grep_shortcut_target': formatting.keyword(' '.join(target_components)),
        })

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return parse_sm_matches.Description.ARGUMENT_USAGE_LIST

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION__MAIN__GREP_SHORTCUT)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [
            syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target,
        ]


def _name__line_matcher(name_of_primitive: str) -> str:
    return ' '.join((
        name_of_primitive,
        syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name,
    ))


_DESCRIPTION__MAIN = """\
Keeps lines matched by {MATCHER},
and discards lines not matched.


{MATCHER} is one of:
"""

_DESCRIPTION__MAIN__EPILOGUE = """\
{Note} {LINE_SEPARATOR_DESCRIPTION}
"""

_DESCRIPTION__LINE_MATCHER = """\
Applies a {_LINE_MATCHER_}.
"""

_DESCRIPTION__LINE_NUMS = """\
A line matches iff it's line number matches any {RANGE}.
"""

_RANGE_EXPR__DESCRIPTION = """\
A consecutive sequence of line numbers.


Negative numbers denote line numbers relative to the end.

-1 is the last line number, 
-2 is the second to last line number, etc. 
"""

_RANGE_EXPR__PROLOGUE = """\
{Note} {FIRST_LINE_NUMBER_DESCRIPTION}


{Note} {INT} must not contain {RANGE_LIMIT_SEPARATOR}
"""

_RANGE_EXPR__DESCRIPTION__INT = """\
The single line number {INT}.
"""

_RANGE_EXPR__DESCRIPTION__LOWER = """\
Line numbers starting from {INT}.
"""

_RANGE_EXPR__DESCRIPTION__UPPER = """\
Line numbers from {FIRST_LINE_NUMBER} to {INT} (including).
"""

_RANGE_EXPR__DESCRIPTION__LOWER_UPPER = """\
Line numbers from {INT} (to the left) to {INT} (to the right) (including).
"""

_DESCRIPTION__MAIN__GREP_SHORTCUT = """\
Shortcut for {grep_shortcut_target}.
"""
