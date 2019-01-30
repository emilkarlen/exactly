from typing import Set

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherBaseNameRegExPattern
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherResolverFromValueParts
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser) -> FileMatcherResolver:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_resolver = parse_regex.parse_regex2(token_parser,
                                                           must_be_on_same_line=True)

    return resolver(regex_resolver)


def resolver(regex_resolver: RegexResolver) -> FileMatcherResolver:
    def get_value(symbols: SymbolTable) -> FileMatcherValue:
        return _Value(regex_resolver.resolve(symbols))

    return FileMatcherResolverFromValueParts(
        regex_resolver.references,
        get_value,
    )


class _Value(FileMatcherValue):
    def __init__(self, regex: RegexValue):
        self._regex = regex

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._regex.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._regex.validator()

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        return FileMatcherBaseNameRegExPattern(self._regex.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> FileMatcher:
        return FileMatcherBaseNameRegExPattern(self._regex.value_of_any_dependency(home_and_sds))
