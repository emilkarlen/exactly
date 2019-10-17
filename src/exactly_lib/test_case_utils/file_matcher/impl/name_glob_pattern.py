from typing import Set, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.description_tree import details as custom_details
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherResolverFromValueParts
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util import strings
from exactly_lib.util.description_tree import details
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


class FileMatcherNameGlobPattern(FileMatcherImplBase):
    """Matches the name (whole path, not just base name) of a path on a shell glob pattern."""

    NAME = 'name matches ' + syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument.name
    VARIANT_NAME = 'matches ' + syntax_elements.GLOB_PATTERN_SYNTAX_ELEMENT.argument.name

    def __init__(self, glob_pattern: str):
        super().__init__()
        self._glob_pattern = glob_pattern
        self._renderer_of_variant = details.HeaderAndValue(
            self.VARIANT_NAME,
            details.String(strings.Repr(glob_pattern))
        )
        self._renderer_of_expected = custom_details.expected(self._renderer_of_variant)

    @property
    def glob_pattern(self) -> str:
        return self._glob_pattern

    @property
    def name(self) -> str:
        return file_matcher.NAME_MATCHER_NAME

    @property
    def option_description(self) -> str:
        return ' '.join([self.name, self._glob_pattern])

    def matches_emr(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        if self.matches(model):
            return None
        else:
            return err_msg_resolvers.of_path(model.path.describer)

    def matches(self, model: FileMatcherModel) -> bool:
        return model.path.primitive.match(self._glob_pattern)

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        tb = self.__tb_with_expected().append_details(
            custom_details.actual(
                custom_details.PathValueAndPrimitiveDetailsRenderer(model.path.describer)
            )

        )
        if model.path.primitive.match(self._glob_pattern):
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
