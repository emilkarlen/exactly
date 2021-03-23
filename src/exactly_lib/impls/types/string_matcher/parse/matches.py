from typing import Sequence

from exactly_lib.definitions import matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.regex import parse_regex
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.impls.types.string_matcher.impl import matches
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(token_parser: TokenParser) -> StringMatcherSdv:
    is_full_match = token_parser.consume_and_handle_optional_option(False,
                                                                    lambda parser: True,
                                                                    matcher_options.FULL_MATCH_ARGUMENT_OPTION)
    regex_sdv = _PARSER_OF_REGEX.parse_from_token_parser(token_parser)

    return matches.sdv(is_full_match, regex_sdv)


_PARSER_OF_REGEX = parse_regex.ParserOfRegex()


class Description(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    ARGUMENT_USAGE_LIST = (
        a.Single(a.Multiplicity.OPTIONAL,
                 a.Option(matcher_options.FULL_MATCH_ARGUMENT_OPTION)),
        syntax_elements.REGEX_SYNTAX_ELEMENT.single_mandatory,
    )

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self.ARGUMENT_USAGE_LIST

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'REGEX': syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
            'full_regex_match': option_syntax.option_syntax(matcher_options.FULL_MATCH_ARGUMENT_OPTION),
            'model': matcher_model.TEXT_MODEL,
        })
        return tp.fnap(_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return syntax_elements.REGEX_SYNTAX_ELEMENT.cross_reference_target,


_DESCRIPTION = """\
Matches iff {REGEX} matches any part of the {model}.


If {full_regex_match} is given,
then {REGEX} must match the full {model}.
"""
