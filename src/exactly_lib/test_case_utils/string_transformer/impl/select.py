from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.line_matcher.model_construction import original_and_model_iter_from_file_line_iter
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer.filter import SelectStringTransformerDdv
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv, StringTransformer, \
    StringTransformerModel
from exactly_lib.util.symbol_table import SymbolTable


class StringTransformerSelectSdv(StringTransformerSdv):
    def __init__(self, line_matcher_sdv: LineMatcherSdv):
        self.line_matcher_sdv = line_matcher_sdv

    def resolve(self, symbols: SymbolTable) -> StringTransformerDdv:
        return SelectStringTransformerDdv(self.line_matcher_sdv.resolve(symbols))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self.line_matcher_sdv.references


def parse_select(parser: TokenParser) -> StringTransformerSdv:
    line_matcher = parse_line_matcher.parse_line_matcher_from_token_parser(parser)
    return StringTransformerSelectSdv(line_matcher)


class SelectStringTransformer(StringTransformer):
    """
    Keeps lines matched by a given :class:`LineMatcher`,
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcher):
        self._line_matcher = line_matcher

    @property
    def name(self) -> str:
        return names.SELECT_TRANSFORMER_NAME

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
