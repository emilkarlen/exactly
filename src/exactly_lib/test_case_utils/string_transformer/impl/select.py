from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.line_matcher.model_construction import original_and_model_iter_from_file_line_iter
from exactly_lib.test_case_utils.string_transformer.filter import SelectStringTransformerValue
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue, StringTransformer, \
    StringTransformerModel
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSelectResolver(StringTransformerResolver):
    def __init__(self, line_matcher_resolver: LineMatcherResolver):
        self.line_matcher_resolver = line_matcher_resolver

    def resolve(self, symbols: SymbolTable) -> StringTransformerValue:
        return SelectStringTransformerValue(self.line_matcher_resolver.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_resolver.references


def parse_select(parser: TokenParser) -> StringTransformerResolver:
    line_matcher = parse_line_matcher.parse_line_matcher_from_token_parser(parser)
    return StringTransformerSelectResolver(line_matcher)


class SelectStringTransformer(StringTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcher):
        self._line_matcher = line_matcher

    @property
    def line_matcher(self) -> LineMatcher:
        return self._line_matcher

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        return (
            line
            for line, line_matcher_model in original_and_model_iter_from_file_line_iter(lines)
            if self._line_matcher.matches(line_matcher_model)
        )

    def __str__(self):
        return '{}({})'.format(type(self).__name__,
                               str(self._line_matcher))
