import re
from typing import Sequence, Set, Pattern, Optional

from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document import parser_classes
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPostSds, \
    PathResolvingEnvironmentPreSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.parse import parse_reg_ex
from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import parse_string_or_here_doc_from_token_parser
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.symbol_table import SymbolTable


def regex_parser() -> Parser[RegexResolver]:
    return _PARSER


def parse_regex(parser: TokenParser) -> RegexResolver:
    parser.require_is_not_at_eol(parse_reg_ex.MISSING_REGEX_ARGUMENT_ERR_MSG)
    is_ignore_case = parser.consume_and_handle_optional_option(False,
                                                               lambda x: True,
                                                               parse_reg_ex.IGNORE_CASE_OPTION_NAME)
    parser.require_is_not_at_eol(parse_reg_ex.MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG)
    source_type, regex_pattern = parse_string_or_here_doc_from_token_parser(parser)
    return _RegexResolver(is_ignore_case, regex_pattern)


_PARSER = parser_classes.ParserFromTokenParserFunction(parse_regex)


class _RegexResolver(RegexResolver):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringResolver):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._validator = _Validator(is_ignore_case, string)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve(self, symbols: SymbolTable) -> RegexValue:
        return _RegexValue(self._is_ignore_case,
                           self._string.resolve(symbols))


class _RegexValue(RegexValue):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringValue):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._pattern = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._string.resolving_dependencies()

    def value_when_no_dir_dependencies(self) -> Pattern:
        if self._pattern is None:
            self._compile_and_set_pattern(self._string.value_when_no_dir_dependencies())
        return self._pattern

    def value_of_any_dependency(self, tcds: HomeAndSds) -> Pattern:
        if self._pattern is None:
            self._compile_and_set_pattern(self._string.value_of_any_dependency(tcds))
        return self._pattern

    def _compile_and_set_pattern(self, regex_pattern: str):
        try:
            flags = 0
            if self._is_ignore_case:
                flags = re.IGNORECASE
            self._pattern = re.compile(regex_pattern, flags)
        except Exception as ex:
            err_msg = "Invalid {}: '{}'".format(instruction_arguments.REG_EX.name, str(ex))
            raise ValueError(err_msg)


class _Validator(PreOrPostSdsValidator):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringResolver):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._hds = None

    def validate_pre_sds_if_applicable(self, environment: PathResolvingEnvironmentPreSds) -> Optional[str]:
        self._hds = environment.hds
        string_value = self._string.resolve(environment.symbols)
        if not string_value.has_dir_dependency():
            string = string_value.value_when_no_dir_dependencies()
            return self._compile(string)
        else:
            return None

    def validate_post_sds_if_applicable(self, environment: PathResolvingEnvironmentPostSds) -> Optional[str]:
        string_value = self._string.resolve(environment.symbols)
        if string_value.has_dir_dependency():
            tcds = HomeAndSds(self._hds, environment.sds)
            string = string_value.value_of_any_dependency(tcds)
            return self._compile(string)
        else:
            return None

    def _compile(self, regex_pattern: str) -> Optional[str]:
        try:
            flags = 0
            if self._is_ignore_case:
                flags = re.IGNORECASE
            re.compile(regex_pattern, flags)
            return None
        except Exception as ex:
            err_msg = "Invalid {}: '{}'".format(instruction_arguments.REG_EX.name, str(ex))
            return err_msg
