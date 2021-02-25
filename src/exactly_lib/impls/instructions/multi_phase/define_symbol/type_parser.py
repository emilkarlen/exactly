from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.test_case.instructions import define_symbol as syntax
from exactly_lib.impls.types.file_matcher import parse_file_matcher
from exactly_lib.impls.types.files_condition import parse as parse_files_condition
from exactly_lib.impls.types.files_matcher import parse_files_matcher
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.line_matcher import parse_line_matcher
from exactly_lib.impls.types.parse import parse_list
from exactly_lib.impls.types.path import parse_path
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionsConfiguration, \
    RelOptionArgumentConfiguration
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.impls.types.string_ import parse_string_or_here_doc
from exactly_lib.impls.types.string_matcher import parse_string_matcher
from exactly_lib.impls.types.string_source import parse as _parse_string_source
from exactly_lib.impls.types.string_transformer import parse_string_transformer
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants


class TypeValueParser:
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        pass


class StringParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_string_or_here_doc.parse_string_or_here_doc_from_token_parser(
            token_parser,
            consume_last_here_doc_line=False,
        )


class PathParser(TypeValueParser):
    def __init__(self):
        self._path_parser = parse_path.PathParser(REL_OPTION_ARGUMENT_CONFIGURATION)

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return self._path_parser.parse_from_token_parser(
            token_parser,
            fs_location_info.current_source_file.abs_path_of_dir_containing_last_file_base_name,
        )


class ListParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_list.parse_list_from_token_parser(token_parser)


class IntegerMatcherParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_integer_matcher.parsers(False).full.parse_from_token_parser(token_parser)


class LineMatcherParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_line_matcher.parsers(False).full.parse_from_token_parser(token_parser)


class FileMatcherParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_file_matcher.parsers().full.parse_from_token_parser(token_parser)


class FilesMatcherParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_files_matcher.parsers().full.parse_from_token_parser(token_parser)


class FilesConditionParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_files_condition.parsers().full.parse_from_token_parser(token_parser)


class StringSourceParser(TypeValueParser):
    _PARSER = _parse_string_source.default_parser_for(
        phase_is_after_act=False,
    )

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return self._PARSER.parse_from_token_parser(token_parser)


class StringMatcherParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_string_matcher.parsers().full.parse_from_token_parser(token_parser)


class StringTransformerParser(TypeValueParser):
    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return parse_string_transformer.parsers().full.parse_from_token_parser(token_parser)


class ProgramParser(TypeValueParser):
    _PARSER = parse_program.program_parser(
        must_be_on_current_line=False,
    )

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              token_parser: TokenParser,
              ) -> SymbolDependentValue:
        return self._PARSER.parse_from_token_parser(token_parser)


REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(
    PathRelativityVariants(frozenset(RelOptionType), True),
    RelOptionType.REL_CWD)

REL_OPTION_ARGUMENT_CONFIGURATION = RelOptionArgumentConfiguration(
    REL_OPTIONS_CONFIGURATION,
    syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
    syntax.PATH_SUFFIX_IS_REQUIRED,
)
