from typing import Iterable, Sequence

from exactly_lib.common.help import headers
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
        _StripTrailingNewLines(),
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
            'Note': headers.NOTE_LINE_HEADER,
            'LINES_ARE_SEPARATED_BY_NEW_LINE': misc_texts.LINES_ARE_SEPARATED_BY_NEW_LINE,
        })
        return tp.fnap(_DESCRIPTION)


class _StripTrailingNewLines(StringTransformerFromLinesTransformer):
    NAME = names.STRIP_TRAILING_NEW_LINES

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
        num_empty_lines_skipped = 0

        for line_before_counted_empty_lines in lines:
            break
        else:
            return

        for next_line in lines:
            if next_line == '\n':
                num_empty_lines_skipped += 1
            else:
                yield line_before_counted_empty_lines
                while num_empty_lines_skipped != 0:
                    yield '\n'
                    num_empty_lines_skipped -= 1
                line_before_counted_empty_lines = next_line

        if line_before_counted_empty_lines[-1] == '\n':
            last_line = line_before_counted_empty_lines[:-1]
        else:
            last_line = line_before_counted_empty_lines
        if last_line != '':
            yield last_line


_DESCRIPTION = """\
Removes every occurrence of {NL} at the end of the {string}.


{Note}
{LINES_ARE_SEPARATED_BY_NEW_LINE}
"""
