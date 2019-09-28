from typing import Set, Pattern, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.err_msg2 import trace_details
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherResolverFromValueParts
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_value import RegexResolver, RegexValue
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.trace.impls.trace_building import TraceBuilder
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


class FileMatcherBaseNameRegExPattern(FileMatcherImplBase):
    """Matches the base name of a path on a regular expression."""

    def __init__(self, compiled_reg_ex: Pattern):
        self._compiled_reg_ex = compiled_reg_ex

    @property
    def name(self) -> str:
        return 'base name matches ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name

    @property
    def reg_ex_pattern(self) -> str:
        return self._compiled_reg_ex.pattern

    @property
    def option_description(self) -> str:
        return 'base name matches regular expression ' + self.reg_ex_pattern

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        if self.matches(model):
            return None
        else:
            return err_msg_resolvers.constant(str(model.path.primitive.name))

    def matches(self, model: FileMatcherModel) -> bool:
        return self._compiled_reg_ex.search(model.path.primitive.name) is not None

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        base_name = model.path.primitive.name
        regex_match = self._compiled_reg_ex.search(base_name)
        tb = self.__tb_with_expected().append_details(
            trace_details.Actual(
                trace_details.ConstantString(base_name)
            )

        )
        if regex_match is not None:
            return tb.build_result(True)
        else:
            return tb.build_result(False)

    def __tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(
            trace_details.Expected(
                trace_details.ConstantString(self._compiled_reg_ex.pattern)
            )
        )
