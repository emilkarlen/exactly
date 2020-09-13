from typing import Iterable, Sequence, Callable

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.expression.grammar import PrimitiveDescription
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl.models.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_to_upper_case(parser: TokenParser) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvConstant(
        _CaseConverter(names.TO_UPPER_CASE,
                       str.upper),
    )


def parse_to_lower_case(parser: TokenParser) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvConstant(
        _CaseConverter(names.TO_LOWER_CASE,
                       str.lower),
    )


def to_upper_case__documentation() -> PrimitiveDescription:
    return _SyntaxDescription('uppercase')


def to_lower_case__documentation() -> PrimitiveDescription:
    return _SyntaxDescription('lowercase')


class _SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, case: str):
        self._case = case

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({'case': self._case})
        return tp.fnap(_DESCRIPTION)


class _CaseConverter(StringTransformerFromLinesTransformer):
    def __init__(self,
                 name: str,
                 converter: Callable[[str], str]
                 ):
        self._name = name
        self._converter = converter
        self._structure = renderers.header_only(name)

    @property
    def name(self) -> str:
        return self._name

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def is_identity_transformer(self) -> bool:
        return False

    def _transform(self, lines: Iterable[str]) -> Iterable[str]:
        return map(self._converter, lines)


_DESCRIPTION = """\
Converts all cased characters to {case}.
"""
