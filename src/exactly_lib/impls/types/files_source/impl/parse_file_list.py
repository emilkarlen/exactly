from typing import Sequence, TypeVar, Generic, Callable, Tuple, Mapping, Optional

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.impls.types.string_source import parse as _parser_str_src
from exactly_lib.section_document.element_parsers.error_messages import MessageFactory
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, ParserFromTokens
from exactly_lib.type_val_deps.types.files_source.sdv import FilesSourceSdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util import functional
from exactly_lib.util.cli_syntax.render.cli_program_syntax import ArgumentUsageOnCommandLineRenderer
from exactly_lib.util.parse import token_matchers
from . import file_list
from .file_makers import regular as _fm_regular, dir_ as _fm_dir
from .. import syntax
from ..file_maker import FileMakerSdv
from ...string_ import parse_string


class Parser(ParserFromTokens[FilesSourceSdv]):
    def __init__(self, parser_of_nested: ParserFromTokens[FilesSourceSdv]):
        self._file_spec_parser = ParserOfFileSpec(parser_of_nested)
        self._superfluous_line_contents_message = _MESSAGE_FACTORY.generator_for(
            _MULTIPLE_FILES_ON_SINGLE_LINE
        )

    def parse(self, token_parser: TokenParser) -> FilesSourceSdv:
        file_specs = self._parse_file_specs(token_parser)

        token_parser.require_has_valid_head_token(_FILE_NAME_OR_SET_END)

        token_parser.consume_mandatory_keyword__part_of_syntax_element(
            syntax.FILE_LIST_END,
            False,
            syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT.singular_name,
        )

        return file_list.Sdv(file_specs)

    def _parse_file_specs(self, token_parser: TokenParser) -> Sequence[file_list.FileSpecificationSdv]:
        ret_val = []
        while not token_parser.has_valid_head_matching(_TOKEN_SPEC_LIST_END):
            ret_val.append(self._file_spec_parser.parse(token_parser))
            if not token_parser.has_valid_head_matching(_TOKEN_SPEC_LIST_END):
                token_parser.require_is_at_eol(self._superfluous_line_contents_message)
        return ret_val


_TOKEN_SPEC_LIST_END = token_matchers.is_unquoted_and_equals(syntax.FILE_LIST_END)

CONTENTS = TypeVar('CONTENTS')


def _mk_file_maker__dir(modification: ModificationType, contents: FilesSourceSdv) -> FileMakerSdv:
    return _fm_dir.DirFileMakerSdv(modification, contents)


def _mk_file_maker__regular_file(modification: ModificationType, contents: StringSourceSdv) -> FileMakerSdv:
    return _fm_regular.RegularFileMakerSdv(modification, contents)


class ParserOfFileMaker(Generic[CONTENTS], ParserFromTokens[FileMakerSdv]):
    _EXPLICIT_CONTENTS_CONFIG = syntax.EXPLICIT_CONTENTS_CONFIG

    _EXPLICIT_CONTENTS_TOKENS = tuple(_EXPLICIT_CONTENTS_CONFIG.keys())

    def __init__(self,
                 contents_parser: ParserFromTokens[CONTENTS],
                 mk_file_maker: Callable[[ModificationType, Optional[CONTENTS]], FileMakerSdv],
                 ):
        self._contents_parser = contents_parser
        self._mk_file_maker = mk_file_maker

    @staticmethod
    def of_directory_maker(parser_of_nested: ParserFromTokens[FilesSourceSdv]) -> ParserFromTokens[FileMakerSdv]:
        return ParserOfFileMaker(
            parser_of_nested,
            _mk_file_maker__dir,
        )

    @staticmethod
    def of_regular_file_maker(phase_is_after_act: bool = False) -> ParserFromTokens[FileMakerSdv]:
        return ParserOfFileMaker(
            _parser_str_src.default_parser_for__tokens(phase_is_after_act),
            _mk_file_maker__regular_file,
        )

    def parse(self, token_parser: TokenParser) -> FileMakerSdv:
        modification_type, contents = self._parse_contents(token_parser)
        return self._mk_file_maker(modification_type, contents)

    def _parse_contents(self, token_parser: TokenParser) -> Tuple[ModificationType, Optional[CONTENTS]]:
        mb_explicit_modification_token = (
            token_parser.consume_optional_constant_string_that_must_be_unquoted_and_equal(
                self._EXPLICIT_CONTENTS_TOKENS,
                must_be_on_current_line=True
            )
        )
        if mb_explicit_modification_token is None:
            return ModificationType.CREATE, None
        else:
            contents = self._contents_parser.parse(token_parser)
            return self._EXPLICIT_CONTENTS_CONFIG[mb_explicit_modification_token], contents


class ParserOfFileSpec(ParserFromTokens[file_list.FileSpecificationSdv]):
    def __init__(self, parser_of_nested: ParserFromTokens[FilesSourceSdv]):
        self._name_parser = parse_string.StringFromTokensParser(_FILE_NAME_STRING_CONFIGURATION)
        self._file_maker_parsers: Mapping[str, ParserFromTokens[FileMakerSdv]] = {
            syntax.REGULAR_FILE_TOKEN: ParserOfFileMaker.of_regular_file_maker(),
            syntax.DIRECTORY_TOKEN: ParserOfFileMaker.of_directory_maker(parser_of_nested),
        }
        self._file_type_tokens = tuple(self._file_maker_parsers.keys())

    def parse(self, token_parser: TokenParser) -> file_list.FileSpecificationSdv:
        file_type_token = self._file_type(token_parser)
        file_name = self._name_parser.parse(token_parser)
        file_maker = self._file_maker_parsers[file_type_token].parse(token_parser)
        return file_list.FileSpecificationSdv(file_name, file_maker)

    def _file_type(self, token_parser: TokenParser) -> str:
        return token_parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
            self._file_type_tokens,
            functional.identity,
            syntax.FILE_TYPE_SE_STR,
        )


_FILE_NAME_STRING_CONFIGURATION = parse_string.Configuration(
    syntax.FILE_NAME.name,
    file_list.FILE_NAME_STRING_REFERENCES_RESTRICTION,
)

_MESSAGE_FACTORY = MessageFactory({
    'FILE_SPEC': syntax.FILE_SPEC__SE_STR,
})

_FILE_NAME_OR_SET_END = ArgumentUsageOnCommandLineRenderer.CHOICE_SEPARATOR.join(
    (syntax.FILE_NAME.name,
     syntax.FILE_LIST_END__FOR_FORMAT_STRINGS)
)

_HEADER = """\
Reading {FILES_SOURCE}"""

_MULTIPLE_FILES_ON_SINGLE_LINE = 'Each {FILE_SPEC} must appear on a separate line.'
