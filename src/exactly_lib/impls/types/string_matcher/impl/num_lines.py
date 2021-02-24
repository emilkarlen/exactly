from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.matcher import property_matcher
from exactly_lib.impls.types.matcher.impls import property_matcher_describers, property_getters
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter, PropertyGetterSdv
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.type_val_deps.types.matcher import MatcherSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers

_NAME = ' '.join((matcher_options.NUM_LINES_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def sdv(matcher: MatcherSdv[int]) -> StringMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matcher,
        _operand_from_model_sdv(),
        property_matcher_describers.GetterWithMatcherAsChild()
    )


class _PropertyGetter(PropertyGetter[StringSource, int], WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: StringSource) -> int:
        ret_val = 0
        with model.contents().as_lines as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_sdv() -> PropertyGetterSdv[StringSource, int]:
    return property_getters.PropertyGetterSdvConstant(
        property_getters.PropertyGetterDdvConstant(
            _PropertyGetter(),
        )
    )
