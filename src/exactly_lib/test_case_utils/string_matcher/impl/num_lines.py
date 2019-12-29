from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import property_matcher_describers, property_getters
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterSdv
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import FileToCheck
from exactly_lib.util.description_tree import renderers

_NAME = ' '.join((matcher_options.NUM_LINES_ARGUMENT,
                  syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.singular_name))


def sdv(matcher: MatcherSdv[int]) -> StringMatcherSdv:
    return StringMatcherSdv(sdv__generic(matcher))


def sdv__generic(matcher: MatcherSdv[int]) -> MatcherSdv[FileToCheck]:
    return property_matcher.PropertyMatcherSdv(
        matcher,
        _operand_from_model_sdv(),
        property_matcher_describers.GetterWithMatcherAsChild()
    )


class _PropertyGetter(PropertyGetter[FileToCheck, int], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(_NAME)

    def get_from(self, model: FileToCheck) -> int:
        ret_val = 0
        with model.lines() as lines:
            for _ in lines:
                ret_val += 1
        return ret_val


def _operand_from_model_sdv() -> PropertyGetterSdv[FileToCheck, int]:
    return property_getters.PropertyGetterSdvConstant(
        property_getters.PropertyGetterDdvConstant(
            _PropertyGetter(),
        )
    )
