from exactly_lib.instructions.utils.file_maker.primitives import FileMaker, FileMakerForConstantContents, \
    FileMakerForContentsFromProgram, FileMakerForContentsFromExistingFile
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.parse import parse_here_document
from exactly_lib.test_case_utils.parse.parse_path import parse_path_from_token_parser
from exactly_lib.test_case_utils.parse.parse_string import parse_string_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.test_case_utils.string_transformer.impl import identity
from exactly_lib.test_case_utils.string_transformer.parse_string_transformer import parse_optional_transformer_sdv
from exactly_lib.util.cli_syntax.option_syntax import is_option_string
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from . import defs


class InstructionConfig:
    def __init__(self,
                 src_rel_opt_arg_conf: RelOptionArgumentConfiguration,
                 syntax_element: str,
                 ):
        self.src_rel_opt_arg_conf = src_rel_opt_arg_conf
        self.syntax_element = syntax_element


def parse_file_contents(instruction_config: InstructionConfig,
                        parser: TokenParser) -> FileMaker:
    """
    Parses a file contents specification of the form: [= FILE-MAKER]

    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    if parser.is_at_eol:
        return FileMakerForConstantContents(string_sdvs.str_constant(''))
    else:
        parser.consume_mandatory_constant_unquoted_string(defs.CONTENTS_ASSIGNMENT_TOKEN, True)
        return parse_file_maker(instruction_config, parser)


def parse_file_maker(instruction_config: InstructionConfig,
                     parser: TokenParser) -> FileMaker:
    parser.require_has_valid_head_token(instruction_config.syntax_element)

    head_source_string = parser.token_stream.head.source_string
    if is_option_string(head_source_string):
        return _parse_file_maker_with_transformation(instruction_config,
                                                     parser)
    else:
        if head_source_string.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
            contents = parse_here_document.parse_as_last_argument_from_token_parser(True,
                                                                                    parser,
                                                                                    False)
            return FileMakerForConstantContents(contents)
        else:
            contents = parse_string_from_token_parser(parser)
            parser.report_superfluous_arguments_if_not_at_eol()
            return FileMakerForConstantContents(contents)


def _parse_file_maker_with_transformation(instruction_config: InstructionConfig,
                                          parser: TokenParser) -> FileMaker:
    def _parse_program_from_stdout(my_parser: TokenParser) -> FileMaker:
        return _parse_program(ProcOutputFile.STDOUT, my_parser)

    def _parse_program_from_stderr(my_parser: TokenParser) -> FileMaker:
        return _parse_program(ProcOutputFile.STDERR, my_parser)

    def _parse_file(my_parser: TokenParser) -> FileMaker:
        src_file = parse_path_from_token_parser(instruction_config.src_rel_opt_arg_conf,
                                                my_parser)
        contents_transformer = parse_optional_transformer_sdv(parser)
        my_parser.report_superfluous_arguments_if_not_at_eol()
        return FileMakerForContentsFromExistingFile(identity.IDENTITY_TRANSFORMER_SDV
                                                    if contents_transformer is None
                                                    else
                                                    contents_transformer,
                                                    src_file)

    def _parse_program(output: ProcOutputFile, my_parser: TokenParser) -> FileMaker:
        is_ignore_exit_code = my_parser.consume_optional_option(defs.IGNORE_EXIT_CODE)
        program = _PROGRAM_PARSER.parse_from_token_parser(my_parser)
        return FileMakerForContentsFromProgram(output,
                                               program,
                                               is_ignore_exit_code)

    return parser.parse_mandatory_option({
        defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDOUT]: _parse_program_from_stdout,
        defs.PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDERR]: _parse_program_from_stderr,
        defs.FILE_OPTION: _parse_file,
    })


_PROGRAM_PARSER = parse_program.program_parser(
    must_be_on_current_line=False,
)
