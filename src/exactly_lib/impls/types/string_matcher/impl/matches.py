from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.matcher import property_matcher
from exactly_lib.impls.types.matcher.impls import matches_regex, property_getters, property_matcher_describers, \
    sdv_components
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter
from exactly_lib.impls.types.regex.regex_ddv import RegexSdv
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherDdv, StringMatcherSdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.symbol_table import SymbolTable


def sdv(is_full_match: bool,
        contents_matcher: RegexSdv) -> StringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> StringMatcherDdv:
        regex_ddv = contents_matcher.resolve(symbols)
        regex_matcher = matches_regex.MatchesRegexDdv(regex_ddv, is_full_match)
        return property_matcher.PropertyMatcherDdv(
            regex_matcher,
            property_getters.PropertyGetterDdvConstant(
                _PropertyGetter(),
            ),
            property_matcher_describers.IdenticalToMatcher(),
        )

    return sdv_components.MatcherSdvFromParts(contents_matcher.references, get_ddv)


class _PropertyGetter(PropertyGetter[StringSource, str], WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only('contents')

    def get_from(self, model: StringSource) -> str:
        return model.contents().as_str
