from typing import Sequence, Iterator

from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.string_transformer import names, sdvs
from exactly_lib.test_case_utils.string_transformer.impl.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse_identity(parser: TokenParser) -> StringTransformerSdv:
    return IDENTITY_TRANSFORMER_SDV


class IdentityStringTransformer(WithCachedTreeStructureDescriptionBase, StringTransformerFromLinesTransformer):
    @property
    def name(self) -> str:
        return names.IDENTITY_TRANSFORMER_NAME

    @property
    def is_identity_transformer(self) -> bool:
        return True

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(names.IDENTITY_TRANSFORMER_NAME)

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return lines


IDENTITY_TRANSFORMER_SDV = sdvs.StringTransformerSdvConstant(IdentityStringTransformer())


class SyntaxDescription(grammar.PrimitiveExpressionDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TEXT_PARSER.fnap(_DESCRIPTION)


_TEXT_PARSER = TextParser()

_DESCRIPTION = """\
Gives output that is identical to the input.
"""
