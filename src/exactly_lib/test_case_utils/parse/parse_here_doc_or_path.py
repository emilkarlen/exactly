import functools
import shlex
from typing import Tuple

from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.string_or_path import StringOrPathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.test_case_utils.parse import parse_here_document, parse_path
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.type_system.data.string_or_path_ddvs import SourceType, StringOrPath
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import option_syntax

CONFIGURATION = parse_path.ALL_REL_OPTIONS_CONFIG

FILE_ARGUMENT_OPTION = a.OptionName(long_name='file')

MISSING_SOURCE = 'Missing argument ({string}, {path} or {here_doc})'.format(
    string=instruction_arguments.STRING.name,
    path=option_syntax(FILE_ARGUMENT_OPTION),
    here_doc=instruction_arguments.HERE_DOCUMENT.name, )


def parse_from_parse_source(source: ParseSource,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION) -> StringOrPathSdv:
    with from_parse_source(source,
                           consume_last_line_if_is_at_eol_after_parse=False) as token_parser:
        ret_val = parse_from_token_parser(token_parser, conf)
    if ret_val.source_type is SourceType.HERE_DOC:
        if source.is_at_eol:
            source.consume_current_line()
    return ret_val


def parse_from_token_parser(token_parser: TokenParser,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION,
                            consume_last_here_doc_line: bool = True) -> StringOrPathSdv:
    token_parser.require_head_token_has_valid_syntax()
    path = token_parser.consume_and_handle_optional_option(
        None,
        functools.partial(parse_path.parse_path_from_token_parser, conf),
        FILE_ARGUMENT_OPTION)
    if path is not None:
        return StringOrPathSdv(SourceType.PATH, None, path)
    else:
        source_type, sdv = parse_string_or_here_doc_from_token_parser(token_parser, consume_last_here_doc_line)
        return StringOrPathSdv(source_type, sdv, None)


def parse_string_or_here_doc_from_token_parser(token_parser: TokenParser,
                                               consume_last_here_doc_line: bool = True
                                               ) -> Tuple[SourceType, StringSdv]:
    token_parser.require_head_token_has_valid_syntax()
    if token_parser.token_stream.head.source_string.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
        here_doc = parse_here_document.parse_as_last_argument_from_token_parser(True, token_parser,
                                                                                consume_last_here_doc_line)
        return SourceType.HERE_DOC, here_doc
    else:
        string_sdv = parse_string.parse_string_from_token_parser(token_parser)
        return SourceType.STRING, string_sdv


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self,
                 prefix: str,
                 expected_contents: StringOrPath):
        self._prefix = prefix
        self.expected_contents = expected_contents

    def resolve(self) -> str:
        prefix = ''
        if self._prefix:
            prefix = self._prefix + ' '
        return prefix + self._expected_obj_description()

    def _expected_obj_description(self) -> str:
        source_type = self.expected_contents.source_type
        if source_type is SourceType.HERE_DOC:
            return instruction_arguments.HERE_DOCUMENT.name
        elif source_type is SourceType.STRING:
            return instruction_arguments.STRING.name + ' ' + self._string_fragment()
        else:
            path_description = self.expected_contents.path_value.describer.value.render()
            return instruction_arguments.FILE_ARGUMENT.name + ' ' + path_description

    def _string_fragment(self) -> str:
        expected = self.expected_contents.string_value
        max_num_chars = 20
        string_fragment = shlex.quote(expected[:max_num_chars])
        if len(expected) > max_num_chars:
            string_fragment += '...'
        return '(' + string_fragment + ')'
