import pathlib

from exactly_lib.instructions.utils import destination_paths as dp
from exactly_lib.instructions.utils.arg_parse.parse_relativity_util import parse_relativity_info
from exactly_lib.instructions.utils.arg_parse.parse_utils import ensure_is_not_option_argument
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import TokenType
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure.destination_path import DestinationPath
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType
from exactly_lib.value_definition.value_structure import ValueReference2


def parse_destination__parse_source(options: RelOptionArgumentConfiguration,
                                    path_argument_is_mandatory: bool,
                                    source: ParseSource) -> DestinationPath:
    token_stream = TokenStream2(source.remaining_source)
    ret_val = parse_destination_path__token_stream(options, path_argument_is_mandatory, token_stream)
    source.consume(token_stream.position)
    return ret_val


def parse_destination_path__token_stream(options: RelOptionArgumentConfiguration,
                                         path_argument_is_mandatory: bool,
                                         source: TokenStream2) -> DestinationPath:
    initial_argument_string = source.remaining_part_of_current_line
    relativity_info = parse_relativity_info(options.options, source)
    if source.is_null:
        if path_argument_is_mandatory:
            raise SingleInstructionInvalidArgumentException(
                'Missing {} argument: {}'.format(options.argument_syntax_name,
                                                 initial_argument_string))
        path_argument = pathlib.PurePath()
        return _from_relativity_info(relativity_info, path_argument)
    else:
        token = source.consume()
        if token.type is TokenType.PLAIN:
            ensure_is_not_option_argument(token.string)
        path_argument = pathlib.PurePosixPath(token.string)
        return _from_relativity_info(relativity_info, path_argument)


def _from_relativity_info(relativity_info, path_argument: pathlib.PurePath) -> DestinationPath:
    if isinstance(relativity_info, RelOptionType):
        return dp.from_rel_option(relativity_info, path_argument)
    elif isinstance(relativity_info, ValueReference2):
        return dp.from_value_reference(relativity_info, path_argument)
