from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_getters, parse_integer_matcher, \
    property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.files_matcher import FilesMatcherModel, FilesMatcherSdvType
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.logic_types import ExpectationType

_NAME = ' '.join((files_matcher_primitives.NUM_FILES_CHECK_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def parse(expectation_type: ExpectationType,
          token_parser: TokenParser) -> FilesMatcherSdv:
    return FilesMatcherSdv(
        parse__generic(expectation_type, token_parser)
    )


def parse__generic(expectation_type: ExpectationType,
                   token_parser: TokenParser) -> FilesMatcherSdvType:
    matcher = parse_integer_matcher.parse(
        token_parser,
        expectation_type,
        parse_integer_matcher.validator_for_non_negative,
    )
    return property_matcher.PropertyMatcherSdv(
        matcher,
        property_getters.sdv_of_constant_primitive(_PropertyGetter()),
        property_matcher_describers.GetterWithMatcherAsChild()
    )


class _PropertyGetter(PropertyGetter[FilesMatcherModel, int], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: FilesMatcherModel) -> int:
        return len(list(model.files()))
