from exactly_lib.impls.types.path.parse_path import parse_path_from_token_parser
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.impls.types.string import parse_here_document
from exactly_lib.impls.types.string.parse_string import parse_string_from_token_parser
from exactly_lib.impls.types.string_model import sdvs
from exactly_lib.impls.types.string_transformer import parse_transformation_option
from exactly_lib.section_document.element_parsers import token_stream_parsing
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.types.string.string_sdv import StringSdv
from exactly_lib.type_val_deps.types.string_model.sdv import StringModelSdv
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.parse.token import Token
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from . import defs
from ..path.rel_opts_configuration import RelOptionsConfiguration, RelOptionArgumentConfiguration


class StringModelParser(ParserFromTokenParserBase[StringModelSdv]):
    def __init__(self, accepted_file_relativities: RelOptionsConfiguration):
        super().__init__(False, False)
        self._variants_parser = token_stream_parsing.ParserOfMandatoryChoiceWithDefault2(
            defs.SYNTAX_ELEMENT,
            [
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.FILE_OPTION),
                    _FileParser(accepted_file_relativities).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDOUT]),
                    _ProgramOutputParser(ProcOutputFile.STDOUT).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    token_matchers.is_option(defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDERR]),
                    _ProgramOutputParser(ProcOutputFile.STDERR).parse,
                ),
                token_stream_parsing.TokenSyntaxSetup2(
                    parse_here_document.HereDocArgTokenMatcher(),
                    _parse_here_doc,
                ),
            ],
            _parse_string,
        )

    def parse_from_token_parser(self, parser: TokenParser) -> StringModelSdv:
        return self._variants_parser.parse(parser)


class _FileParser:
    def __init__(self, accepted_file_relativities: RelOptionsConfiguration):
        self._relativities_arg_conf = RelOptionArgumentConfiguration(
            accepted_file_relativities,
            defs.SOURCE_FILE_ARGUMENT_NAME,
            True,
        )

    def parse(self, file_option: Token, token_parser: TokenParser) -> StringModelSdv:
        src_file = parse_path_from_token_parser(self._relativities_arg_conf, token_parser)
        src_file_model = sdvs.PathStringModelSdv(src_file)
        optional_transformer = parse_transformation_option.parse_optional_option__optional(token_parser)

        return (
            src_file_model
            if optional_transformer is None
            else
            sdvs.TransformedStringModelSdv(
                src_file_model,
                optional_transformer,
            )
        )


class _ProgramOutputParser:
    def __init__(self, output_file_to_capture: ProcOutputFile):
        self._output_file_to_capture = output_file_to_capture

    def parse(self, program_option: Token, token_parser: TokenParser) -> StringModelSdv:
        is_ignore_exit_code = token_parser.consume_optional_option(defs.IGNORE_EXIT_CODE)
        program = _PROGRAM_PARSER.parse_from_token_parser(token_parser)


def _parse_here_doc(here_doc_start_token: Token, parser: TokenParser) -> StringModelSdv:
    return _of_string(
        parse_here_document.parse_document_of_start_str(here_doc_start_token.string, parser, False)
    )


def _parse_string(parser: TokenParser) -> StringModelSdv:
    return _of_string(parse_string_from_token_parser(parser))


def _of_string(contents: StringSdv) -> StringModelSdv:
    return sdvs.ConstantStringStringModelSdv(contents)


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)
