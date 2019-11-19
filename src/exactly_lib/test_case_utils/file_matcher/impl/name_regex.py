from typing import Pattern, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherSdvFromValueParts
from exactly_lib.test_case_utils.regex import parse_regex
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details
from exactly_lib.util.symbol_table import SymbolTable


def parse(token_parser: TokenParser) -> FileMatcherSdv:
    token_parser.require_has_valid_head_token(syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name)
    source_type, regex_sdv = parse_regex.parse_regex2(token_parser,
                                                      must_be_on_same_line=True)

    return sdv(regex_sdv)


def sdv(regex_sdv: RegexSdv) -> FileMatcherSdv:
    def get_value(symbols: SymbolTable) -> FileMatcherDdv:
        return _Ddv(regex_sdv.resolve(symbols))

    return FileMatcherSdvFromValueParts(
        regex_sdv.references,
        get_value,
    )


class _Ddv(FileMatcherDdv):
    def __init__(self, regex: RegexDdv):
        self._regex = regex

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._regex.validator()

    def value_of_any_dependency(self, tcds: Tcds) -> FileMatcher:
        return FileMatcherBaseNameRegExPattern(self._regex.value_of_any_dependency(tcds))


class FileMatcherBaseNameRegExPattern(FileMatcherImplBase):
    """Matches the base name of a path on a regular expression."""

    VARIANT_NAME = 'matches ' + syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name

    def __init__(self, compiled_reg_ex: Pattern):
        super().__init__()
        self._compiled_reg_ex = compiled_reg_ex
        self._renderer_of_variant = details.HeaderAndValue(
            self.VARIANT_NAME,
            details.String(strings.Repr(compiled_reg_ex.pattern))
        )
        self._renderer_of_expected = custom_details.expected(self._renderer_of_variant)

    @property
    def name(self) -> str:
        return file_matcher.NAME_MATCHER_NAME

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
            custom_details.actual(
                details.String(base_name)
            )

        )
        if regex_match is not None:
            return tb.build_result(True)
        else:
            return tb.build_result(False)

    def _structure(self) -> StructureRenderer:
        return (
            self._new_structure_builder()
                .append_details(self._renderer_of_variant)
                .build()
        )

    def __tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._renderer_of_expected)
