from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, property_getters, property_matcher_describers, \
    sdv_components
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.test_case_utils.string_matcher.impl import sdvs
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import StringMatcherDdv, FileToCheck, GenericStringMatcherSdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def sdv(expectation_type: ExpectationType,
        is_full_match: bool,
        contents_matcher: RegexSdv) -> StringMatcherSdv:
    return sdvs.new_maybe_negated(
        sdv__generic(is_full_match, contents_matcher),
        expectation_type,
    )


def sdv__generic(is_full_match: bool,
                 contents_matcher: RegexSdv) -> GenericStringMatcherSdv:
    def get_ddv(symbols: SymbolTable) -> StringMatcherDdv:
        regex_ddv = contents_matcher.resolve(symbols)
        regex_matcher = matches_regex.MatchesRegexDdv(ExpectationType.POSITIVE, regex_ddv, is_full_match)
        return property_matcher.PropertyMatcherDdv(
            regex_matcher,
            property_getters.PropertyGetterDdvConstant(
                _PropertyGetter(),
            ),
            property_matcher_describers.IdenticalToMatcher(),
        )

    return sdv_components.MatcherSdvFromParts(contents_matcher.references, get_ddv)


class _PropertyGetter(PropertyGetter[FileToCheck, str], WithCachedTreeStructureDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only('contents')

    def get_from(self, model: FileToCheck) -> str:
        with model.lines() as lines:
            return ''.join(lines)
