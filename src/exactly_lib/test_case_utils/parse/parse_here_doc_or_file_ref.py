import functools
import pathlib
import shlex
from typing import Tuple

from exactly_lib.definitions import instruction_arguments
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser, \
    from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.error_messages import path_resolving_env_from_err_msg_env
from exactly_lib.symbol.data.string_or_file import StringOrFileRefResolver
from exactly_lib.type_system.data.string_or_file_ref_values import SourceType
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.err_msg import diff_msg_utils
from exactly_lib.type_system.data.path_description import path_value_with_relativity_name_prefix
from exactly_lib.test_case_utils.parse import parse_here_document, parse_file_ref
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import option_syntax

CONFIGURATION = parse_file_ref.ALL_REL_OPTIONS_CONFIG

FILE_ARGUMENT_OPTION = a.OptionName(long_name='file')

MISSING_SOURCE = 'Missing argument ({string}, {file_ref} or {here_doc})'.format(
    string=instruction_arguments.STRING.name,
    file_ref=option_syntax(FILE_ARGUMENT_OPTION),
    here_doc=instruction_arguments.HERE_DOCUMENT.name, )


def parse_from_parse_source(source: ParseSource,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION) -> StringOrFileRefResolver:
    with from_parse_source(source,
                           consume_last_line_if_is_at_eol_after_parse=False) as token_parser:
        ret_val = parse_from_token_parser(token_parser, conf)
    if ret_val.source_type is SourceType.HERE_DOC:
        if source.is_at_eol:
            source.consume_current_line()
    return ret_val


def parse_from_token_parser(token_parser: TokenParser,
                            conf: RelOptionArgumentConfiguration = CONFIGURATION,
                            consume_last_here_doc_line: bool = True) -> StringOrFileRefResolver:
    token_parser.require_head_token_has_valid_syntax()
    file_ref = token_parser.consume_and_handle_optional_option(
        None,
        functools.partial(parse_file_ref.parse_file_ref_from_token_parser, conf),
        FILE_ARGUMENT_OPTION)
    if file_ref is not None:
        return StringOrFileRefResolver(SourceType.PATH, None, file_ref)
    else:
        source_type, resolver = parse_string_or_here_doc_from_token_parser(token_parser, consume_last_here_doc_line)
        return StringOrFileRefResolver(source_type, resolver, None)


def parse_string_or_here_doc_from_token_parser(token_parser: TokenParser,
                                               consume_last_here_doc_line: bool = True
                                               ) -> Tuple[SourceType, StringResolver]:
    token_parser.require_head_token_has_valid_syntax()
    if token_parser.token_stream.head.source_string.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
        here_doc = parse_here_document.parse_as_last_argument_from_token_parser(True, token_parser,
                                                                                consume_last_here_doc_line)
        return SourceType.HERE_DOC, here_doc
    else:
        string_resolver = parse_string.parse_string_from_token_parser(token_parser)
        return SourceType.STRING, string_resolver


class ExpectedValueResolver(diff_msg_utils.ExpectedValueResolver):
    def __init__(self,
                 prefix: str,
                 expected_contents: StringOrFileRefResolver):
        self._prefix = prefix
        self.expected_contents = expected_contents

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        prefix = ''
        if self._prefix:
            prefix = self._prefix + ' '
        return prefix + self._expected_obj_description(environment)

    def _expected_obj_description(self, environment: ErrorMessageResolvingEnvironment) -> str:
        resolving_env = path_resolving_env_from_err_msg_env(environment)
        source_type = self.expected_contents.source_type
        if source_type is SourceType.HERE_DOC:
            return instruction_arguments.HERE_DOCUMENT.name
        elif source_type is SourceType.STRING:
            return instruction_arguments.STRING.name + ' ' + self._string_fragment(resolving_env)
        else:
            path_value = self.expected_contents.file_reference_resolver.resolve(resolving_env.symbols)
            path_description = path_value_with_relativity_name_prefix(path_value,
                                                                      resolving_env.home_and_sds,
                                                                      pathlib.Path.cwd())
            return instruction_arguments.FILE_ARGUMENT.name + ' ' + path_description

    def _string_fragment(self, environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        expected = self.expected_contents.string_resolver.resolve_value_of_any_dependency(environment)
        max_num_chars = 20
        string_fragment = shlex.quote(expected[:max_num_chars])
        if len(expected) > max_num_chars:
            string_fragment += '...'
        return '(' + string_fragment + ')'
