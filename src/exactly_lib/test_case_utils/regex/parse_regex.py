import re
from typing import Sequence, Set, Pattern, Optional, Tuple

from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.ps_or_tp import parsers
from exactly_lib.section_document.element_parsers.ps_or_tp.parser import Parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.parse.parse_here_doc_or_path import parse_string_or_here_doc_from_token_parser
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.type_system.data.string_or_path_ddvs import SourceType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.render import strings as string_rendering
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.symbol_table import SymbolTable

IGNORE_CASE_OPTION_NAME = a.OptionName(long_name='ignore-case')

IGNORE_CASE_OPTION = option_syntax.option_syntax(IGNORE_CASE_OPTION_NAME)

MISSING_REGEX_ARGUMENT_ERR_MSG = 'Missing ' + syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name

MISSING_STRING_ARGUMENT_FOR_REGEX_ERR_MSG = 'Missing {} argument for {}'.format(
    syntax_elements.STRING_SYNTAX_ELEMENT.argument.name,
    syntax_elements.REGEX_SYNTAX_ELEMENT.argument.name,
)


def regex_parser() -> Parser[RegexSdv]:
    return _PARSER


def parse_regex(parser: TokenParser,
                must_be_on_same_line: bool = True,
                consume_last_here_doc_line: bool = False) -> RegexSdv:
    return parse_regex2(parser, must_be_on_same_line, consume_last_here_doc_line)[1]


def parse_regex2(parser: TokenParser,
                 must_be_on_same_line: bool = True,
                 consume_last_here_doc_line: bool = False) -> Tuple[SourceType, RegexSdv]:
    if must_be_on_same_line:
        parser.require_is_not_at_eol(MISSING_REGEX_ARGUMENT_ERR_MSG)

    is_ignore_case = parser.consume_and_handle_optional_option(False,
                                                               lambda x: True,
                                                               IGNORE_CASE_OPTION_NAME)
    if must_be_on_same_line:
        parser.require_is_not_at_eol(MISSING_REGEX_ARGUMENT_ERR_MSG)

    source_type, regex_pattern = parse_string_or_here_doc_from_token_parser(parser,
                                                                            consume_last_here_doc_line)
    return source_type, _RegexSdv(is_ignore_case, regex_pattern)


_PARSER = parsers.ParserFromTokenParserFunction(parse_regex)


class _RegexSdv(RegexSdv):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringSdv):
        self._is_ignore_case = is_ignore_case
        self._string = string
        self._value = None

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._string.references

    def resolve(self, symbols: SymbolTable) -> RegexDdv:
        return _RegexDdv(self._is_ignore_case,
                         self._string.resolve(symbols))


class _ValidatorWhichCreatesRegex(DdvValidator):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringDdv):
        self._is_ignore_case = is_ignore_case
        self.string = string
        self.pattern = None

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self.string.resolving_dependencies()

    def validate_pre_sds_if_applicable(self, hds: HomeDirectoryStructure) -> Optional[TextRenderer]:
        if self.pattern is None:
            if not self.string.resolving_dependencies():
                return self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        else:
            return None

    def validate_post_sds_if_applicable(self, tcds: Tcds) -> Optional[TextRenderer]:
        if self.pattern is None:
            return self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        else:
            return None

    def pattern_when_no_dir_dependencies(self) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_when_no_dir_dependencies())
        return self.pattern

    def pattern_of_any_dependency(self, tcds: Tcds) -> Pattern:
        if self.pattern is None:
            self._compile_and_set_pattern(self.string.value_of_any_dependency(tcds))
        return self.pattern

    def _compile_and_set_pattern(self, regex_pattern: str) -> Optional[TextRenderer]:
        try:
            flags = 0
            if self._is_ignore_case:
                flags = re.IGNORECASE
            self.pattern = re.compile(regex_pattern, flags)
            return None
        except Exception as ex:
            return text_docs.single_line(
                str_constructor.FormatPositional(
                    "Invalid {}: '{}'",
                    instruction_arguments.REG_EX.name,
                    ex,
                )
            )


class _RegexDdv(RegexDdv):
    def __init__(self,
                 is_ignore_case: bool,
                 string: StringDdv,
                 ):
        self._describer = custom_details.regex(
            is_ignore_case,
            details.String(string_rendering.AsToStringObject(string.describer()))
        )
        self._validator = _ValidatorWhichCreatesRegex(is_ignore_case, string)

    def describer(self) -> DetailsRenderer:
        return self._describer

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._validator.resolving_dependencies()

    def validator(self) -> DdvValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> Pattern:
        return self._validator.pattern_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: Tcds) -> Pattern:
        return self._validator.pattern_of_any_dependency(tcds)
