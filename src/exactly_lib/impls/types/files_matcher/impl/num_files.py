from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.matcher import property_matcher
from exactly_lib.impls.types.matcher.impls import property_getters, property_matcher_describers
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcherModel
from exactly_lib.util.description_tree import renderers

_NAME = ' '.join((config.NUM_FILES_CHECK_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def parser() -> ParserFromTokens[FilesMatcherSdv]:
    return _PARSER


class _Parser(ParserFromTokens[FilesMatcherSdv]):
    def __init__(self):
        self._integer_matcher_parser = parse_integer_matcher.parsers(False).simple

    def parse(self, token_parser: TokenParser) -> FilesMatcherSdv:
        matcher = self._integer_matcher_parser.parse_from_token_parser(token_parser)
        return property_matcher.PropertyMatcherSdv(
            matcher,
            property_getters.sdv_of_constant_primitive(_PropertyGetter()),
            property_matcher_describers.GetterWithMatcherAsChild()
        )


_PARSER = _Parser()


class _PropertyGetter(PropertyGetter[FilesMatcherModel, int], WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: FilesMatcherModel) -> int:
        ret_val = 0
        for _ in model.files():
            ret_val += 1

        return ret_val
