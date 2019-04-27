from typing import Set, Pattern, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherResolverFromValueParts
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
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


class FileMatcherBaseNameRegExPattern(FileMatcher):
    """Matches the base name of a path on a regular expression."""

    def __init__(self, compiled_reg_ex: Pattern):
        self._compiled_reg_ex = compiled_reg_ex

    @property
    def reg_ex_pattern(self) -> str:
        return self._compiled_reg_ex.pattern

    @property
    def option_description(self) -> str:
        return 'base name matches regular expression ' + self.reg_ex_pattern

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        if self.matches(model):
            return None
        else:
            return err_msg_resolvers.constant(str(model.path.name))

    def matches(self, model: FileMatcherModel) -> bool:
        return self._compiled_reg_ex.search(model.path.name) is not None