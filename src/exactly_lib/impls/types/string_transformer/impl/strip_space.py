from typing import Iterable, Sequence, Callable

from exactly_lib.common.help import headers
from exactly_lib.definitions import doc_format, matcher_model
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.expression import grammar
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.impls.types.string_transformer import sdvs
from exactly_lib.impls.types.string_transformer.impl.sources.transformed_string_sources import \
    StringTransformerFromLinesTransformer
from exactly_lib.section_document.element_parsers import token_stream_parsing
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.section_document.element_parsers.token_stream_parsing import TokenSyntaxSetup
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class Parser(ParserFromTokens[StringTransformerSdv]):
    def __init__(self):
        self._parser_of_primitive = token_stream_parsing.ParserOfOptionalChoiceWithDefault(
            [
                self._setup_of_variant(
                    names.STRIP_TRAILING_NEW_LINES_OPTION_NAME,
                    _strip_trailing_new_lines,
                ),
                self._setup_of_variant(
                    names.STRIP_TRAILING_SPACE_OPTION_NAME,
                    _strip_trailing_space,
                ),
            ],
            self._parse_default_variant,
        )

    def parse(self, token_parser: TokenParser) -> StringTransformerSdv:
        return sdvs.StringTransformerSdvConstant(
            self._parser_of_primitive.parse(token_parser)
        )

    @staticmethod
    def _setup_of_variant(option: a.OptionName,
                          transformer: Callable[[Iterable[str]], Iterable[str]],
                          ) -> TokenSyntaxSetup[StringTransformer]:
        def parse_variant(token_parser: TokenParser) -> StringTransformer:
            return _StripWhiteSpaceTransformer(
                custom_details.OptionNameRenderer(option),
                transformer,
            )

        return TokenSyntaxSetup(
            token_matchers.is_option(option),
            parse_variant,
        )

    @staticmethod
    def _parse_default_variant(token_parser: TokenParser) -> StringTransformer:
        return _StripWhiteSpaceTransformer(
            details.empty(),
            _strip_space,
        )


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Choice.of_single_argument_choices(
                a.Multiplicity.OPTIONAL,
                [
                    a.Option(names.STRIP_TRAILING_SPACE_OPTION_NAME),
                    a.Option(names.STRIP_TRAILING_NEW_LINES_OPTION_NAME),
                ],
            )
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'NL': misc_texts.NEW_LINE_STRING_CONSTANT,
            'model': matcher_model.TEXT_MODEL,
            'white_space': misc_texts.WHITESPACE,
            'Note': headers.NOTE_LINE_HEADER,
            'LINES_ARE_SEPARATED_BY_NEW_LINE': misc_texts.LINES_ARE_SEPARATED_BY_NEW_LINE,
            'trailing_new_lines_option': formatting.argument_option(names.STRIP_TRAILING_NEW_LINES_OPTION_NAME),
            'trailing_space_option': formatting.argument_option(names.STRIP_TRAILING_SPACE_OPTION_NAME),
        })
        return tp.fnap(_DESCRIPTION__MAIN) + [self._options_table(tp)]

    @staticmethod
    def _options_table(tp: TextParser) -> ParagraphItem:
        def item(option: a.OptionName, description_template: str) -> lists.HeaderContentListItem:
            return docs.list_item(
                doc_format.syntax_text(option_syntax.option_syntax(option)),
                tp.fnap(description_template)
            )

        return docs.simple_list_with_space_between_elements_and_content(
            [
                item(names.STRIP_TRAILING_SPACE_OPTION_NAME, _DESCRIPTION__TRAILING_SPACE),
                item(names.STRIP_TRAILING_NEW_LINES_OPTION_NAME, _DESCRIPTION__TRAILING_NEW_LINES),
            ],
            lists.ListType.VARIABLE_LIST,
        )


class _StripWhiteSpaceTransformer(StringTransformerFromLinesTransformer):
    NAME = names.STRIP_SPACE

    def __init__(self,
                 variant_description: DetailsRenderer,
                 transformer: Callable[[Iterable[str]], Iterable[str]],
                 ):
        self._transformer = transformer
        self._structure = (
            StructureBuilder(self.NAME)
                .append_details(variant_description)
                .build()
        )

    @property
    def name(self) -> str:
        return self.NAME

    def structure(self) -> StructureRenderer:
        return self._structure

    @property
    def is_identity_transformer(self) -> bool:
        return False

    def _transformation_may_depend_on_external_resources(self) -> bool:
        return False

    def _transform(self, lines: Iterable[str]) -> Iterable[str]:
        return self._transformer(lines)


def _strip_space(lines: Iterable[str]) -> Iterable[str]:
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


def _strip_trailing_space(lines: Iterable[str]) -> Iterable[str]:
    empty_lines_skipped = []

    for line_before_empty_lines_list in lines:
        break
    else:
        return

    for next_line in lines:
        if next_line.isspace():
            empty_lines_skipped.append(next_line)
        else:
            yield line_before_empty_lines_list
            for empty_line in empty_lines_skipped:
                yield empty_line
            empty_lines_skipped = []
            line_before_empty_lines_list = next_line

    mb_last = line_before_empty_lines_list.rstrip()
    if mb_last != '':
        yield mb_last


def _strip_trailing_new_lines(lines: Iterable[str]) -> Iterable[str]:
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


_DESCRIPTION__MAIN = """\
Removes all {white_space} at the beginning and end of the {model} (by default).
"""

_DESCRIPTION__TRAILING_SPACE = """\
Removes all {white_space} at the end of the {model}.
"""

_DESCRIPTION__TRAILING_NEW_LINES = """\
Removes every {NL} at the end of the {model}.


{Note}
{LINES_ARE_SEPARATED_BY_NEW_LINE}
"""
