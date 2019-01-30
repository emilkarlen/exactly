from typing import Set

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherResolverFromValueParts
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser) -> FileMatcherResolver:
    glob_pattern = parse_string.parse_string_from_token_parser(token_parser, _PARSE_STRING_CONFIGURATION)

    return resolver(glob_pattern)


_PARSE_STRING_CONFIGURATION = parse_string.Configuration(syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.singular_name,
                                                         reference_restrictions=None)


def resolver(glob_pattern: StringResolver) -> FileMatcherResolver:
    def get_value(symbols: SymbolTable) -> FileMatcherValue:
        return _Value(glob_pattern.resolve(symbols))

    return FileMatcherResolverFromValueParts(
        glob_pattern.references,
        get_value,
    )


class _Value(FileMatcherValue):
    def __init__(self, glob_pattern: StringValue):
        self._glob_pattern = glob_pattern

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._glob_pattern.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        return FileMatcherNameGlobPattern(self._glob_pattern.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> FileMatcher:
        return FileMatcherNameGlobPattern(self._glob_pattern.value_of_any_dependency(home_and_sds))
