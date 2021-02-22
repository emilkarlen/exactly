from typing import Sequence

from exactly_lib.definitions import formatting, matcher_model
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.path import path_relativities
from exactly_lib.impls.types.string_matcher.impl import equality
from exactly_lib.impls.types.string_source import parse as parse_str_src
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import PARSE_RESULT
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser

REL_OPT_CONFIG = path_relativities.all_rel_options_config(RelOptionType.REL_HDS_CASE)


class EqualsParser(ParserFromTokenParserBase[StringMatcherSdv]):
    def __init__(self):
        super().__init__(False, False)
        self._str_src_parser = parse_str_src.string_source_parser(REL_OPT_CONFIG)

    def parse_from_token_parser(self, parser: TokenParser) -> PARSE_RESULT:
        expected_contents = self._str_src_parser.parse_from_token_parser(parser)

        return equality.sdv(expected_contents)


class Description(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.single_mandatory
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'STRING_SOURCE': formatting.syntax_element_(syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT),
            'model': matcher_model.TEXT_MODEL,
        })
        return tp.fnap(_DESCRIPTION)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return [
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.cross_reference_target
        ]


_DESCRIPTION = """\
Matches iff the {model} is equal to {STRING_SOURCE}.
"""
