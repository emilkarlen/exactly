from typing import Sequence, Callable, Iterator

from exactly_lib.definitions import doc_format
from exactly_lib.definitions.argument_rendering import cl_syntax
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
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class Parser(ParserFromTokens[StringTransformerSdv]):
    def __init__(self):
        self._parser_of_primitive = token_stream_parsing.ParserOfMandatoryChoice(
            cl_syntax.cl_syntax_for_args((SyntaxDescription.OPTION_SYNTAX_ELEMENT,)),
            [
                self._setup_of_variant(
                    names.CHARACTER_CASE_TO_LOWER_OPTION_NAME,
                    str.lower,
                ),
                self._setup_of_variant(
                    names.CHARACTER_CASE_TO_UPPER_OPTION_NAME,
                    str.upper,
                ),
            ],
        )

    def parse(self, token_parser: TokenParser) -> StringTransformerSdv:
        return sdvs.StringTransformerSdvConstant(
            self._parser_of_primitive.parse(token_parser)
        )

    @staticmethod
    def _setup_of_variant(option: a.OptionName,
                          converter: Callable[[str], str],
                          ) -> TokenSyntaxSetup[StringTransformer]:
        def parse_variant(token_parser: TokenParser) -> StringTransformer:
            return _CaseConverter(
                custom_details.OptionNameRenderer(option),
                converter,
            )

        return TokenSyntaxSetup(
            token_matchers.is_option(option),
            parse_variant,
        )


class SyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    OPTION_SYNTAX_ELEMENT = a.Choice.of_single_argument_choices(
        a.Multiplicity.MANDATORY,
        [
            a.Option(names.CHARACTER_CASE_TO_LOWER_OPTION_NAME),
            a.Option(names.CHARACTER_CASE_TO_UPPER_OPTION_NAME),
        ])

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return (self.OPTION_SYNTAX_ELEMENT,)

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return [self._options_table()]

    @staticmethod
    def _options_table() -> ParagraphItem:
        return docs.simple_list_with_space_between_elements_and_content(
            [
                SyntaxDescription._item(names.CHARACTER_CASE_TO_LOWER_OPTION_NAME,
                                        TextParser({'case': _CASE__LOWER})),
                SyntaxDescription._item(names.CHARACTER_CASE_TO_UPPER_OPTION_NAME,
                                        TextParser({'case': _CASE__UPPER})),
            ],
            lists.ListType.VARIABLE_LIST,
        )

    @staticmethod
    def _item(option: a.OptionName,
              tp: TextParser,
              ) -> lists.HeaderContentListItem:
        return docs.list_item(
            doc_format.syntax_text(option_syntax.option_syntax(option)),
            tp.fnap(_DESCRIPTION)
        )


class _CaseConverter(StringTransformerFromLinesTransformer):
    NAME = names.CHARACTER_CASE

    def __init__(self,
                 variant_description: DetailsRenderer,
                 converter: Callable[[str], str]
                 ):
        self._converter = converter
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

    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        return map(self._converter, lines)


_CASE__LOWER = 'lowercase'
_CASE__UPPER = 'uppercase'

_DESCRIPTION = """\
Converts all cased characters to {case}.
"""
