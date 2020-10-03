from pathlib import Path

from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_utils.matcher import property_matcher
from exactly_lib.test_case_utils.matcher.impls import matches_regex, matches_glob_pattern, \
    property_getters, property_matcher_describers
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcherSdv


def reg_ex_sdv(property_getter: PropertyGetter[FileMatcherModel, str],
               regex: RegexSdv) -> FileMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matches_regex.MatchesRegexSdv(regex, False),
        property_getters.sdv_of_constant_primitive(
            property_getter,
        ),
        property_matcher_describers.GetterWithMatcherAsDetail(),
    )


def glob_pattern_sdv(property_getter: PropertyGetter[FileMatcherModel, Path],
                     glob_pattern: StringSdv) -> FileMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matches_glob_pattern.sdv__path(glob_pattern),
        property_getters.sdv_of_constant_primitive(
            property_getter,
        ),
        property_matcher_describers.GetterWithMatcherAsDetail(),
    )


def glob_pattern_sdv__str(property_getter: PropertyGetter[FileMatcherModel, str],
                          glob_pattern: StringSdv) -> FileMatcherSdv:
    return property_matcher.PropertyMatcherSdv(
        matches_glob_pattern.sdv__str(glob_pattern),
        property_getters.sdv_of_constant_primitive(
            property_getter,
        ),
        property_matcher_describers.GetterWithMatcherAsDetail(),
    )
