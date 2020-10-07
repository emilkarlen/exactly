from typing import Iterable, Sequence

from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import types
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.expression import grammar
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer import sdvs
from exactly_lib.test_case_utils.string_transformer.impl.models.transformed_string_models import \
    StringTransformerFromLinesTransformer
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def parse(token_parser: TokenParser) -> StringTransformerSdv:
    return sdvs.StringTransformerSdvConstant(
        _StripWhiteSpace(),
    )


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'NL': misc_texts.NEW_LINE_STRING_CONSTANT,
            'string': types.STRING_TYPE_INFO.singular_name,
            'white_space': misc_texts.WHITESPACE,
        })
        return tp.fnap(_DESCRIPTION)


class _StripWhiteSpace(StringTransformerFromLinesTransformer):
    NAME = names.STRIP_SPACE

    def __init__(self):
        self._structure = renderers.header_only(self.NAME)

    @property
    def name(self) -> str:
        return self.NAME

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def is_identity_transformer(self) -> bool:
        return False

    def _transform(self, lines: Iterable[str]) -> Iterable[str]:
        empty_lines_skipped = []

        for non_empty_line in lines:
            if not non_empty_line.isspace():
                break
        else:
            return

        non_empty_line = non_empty_line.lstrip()

        for next_line in lines:
            if next_line.isspace():
                empty_lines_skipped.append(next_line)
            else:
                yield non_empty_line
                for empty_line in empty_lines_skipped:
                    yield empty_line
                empty_lines_skipped = []
                non_empty_line = next_line

        yield non_empty_line.rstrip()


_DESCRIPTION = """\
Removes all {white_space} at the beginning and end of the {string}.
"""
