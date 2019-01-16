import re
from typing import Sequence, Set, Pattern, Optional, Tuple

from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.program.string_or_file import SourceType
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import parse_string_or_here_doc_from_token_parser
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.symbol_table import SymbolTable


def regex_parser() -> Parser[RegexResolver]:
    return _PARSER


def parse_regex(parser: TokenParser) -> RegexResolver:
    return parse_regex2(parser)[1]


def parse_regex2(parser: TokenParser,
                 must_be_on_same_line: bool = True) -> Tuple[SourceType, RegexResolver]:
    if must_be_on_same_line:
        parser.require_is_not_at_eol(parse_reg_ex.MISSING_REGEX_ARGUMENT_ERR_MSG)

    is_ignore_case = parser.consume_and_handle_optional_option(False,
                                                               lambda x: True,
                                                               parse_reg_ex.IGNORE_CASE_OPTION_NAME)
    if must_be_on_same_line:
        parser.require_is_not_at_eol(parse_reg_ex.MISSING_REGEX_ARGUMENT_ERR_MSG)

    source_type, regex_pattern = parse_string_or_here_doc_from_token_parser(parser)
    return source_type, _RegexResolver(is_ignore_case, regex_pattern)


_PARSER = parser_classes.ParserFromTokenParserFunction(parse_regex)


class _RegexResolver(RegexResolver):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringResolver):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._value = None

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def resolve(self, symbols: SymbolTable) -> RegexValue:
        return _RegexValue(self._is_ignore_case,
                           self._string.resolve(symbols))


class _ValidatorWhichCreatesRegex(PreOrPostSdsValueValidator):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringValue):
        self._is_ignore_case = is_ignore_case
        self.string = string
        self.pattern = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self.string.resolving_dependencies()

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[str]:
        if self.pattern is None:
            if not self.string.resolving_dependencies():
                return self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        else:
            return None

    def validate_post_sds_if_applicable(self, tcds: HomeAndSds) -> Optional[str]:
        if self.pattern is None:
            return self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        else:
            return None

    def pattern_when_no_dir_dependencies(self) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        return self.pattern

    def pattern_of_any_dependency(self, tcds: HomeAndSds) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        return self.pattern

    def _compile_and_set_pattern(self, regex_pattern: str) -> Optional[str]:
        try:
            flags = 0
            if self._is_ignore_case:
                flags = re.IGNORECASE
            self.pattern = re.compile(regex_pattern, flags)
            return None
        except Exception as ex:
            err_msg = "Invalid {}: '{}'".format(instruction_arguments.REG_EX.name, str(ex))
            return err_msg


class _RegexValue(RegexValue):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringValue):
        self._validator = _ValidatorWhichCreatesRegex(is_ignore_case, string)

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._validator.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> Pattern:
        return self._validator.pattern_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: HomeAndSds) -> Pattern:
        return self._validator.pattern_of_any_dependency(tcds)
