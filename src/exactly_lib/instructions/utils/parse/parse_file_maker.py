from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args, \
    cli_argument_syntax_element_description
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.instructions.utils.file_maker import FileMaker, FileMakerForConstantContents, \
    FileMakerForContentsFromProgram, FileMakerForContentsFromExistingFile
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.test_case_utils.parse import parse_here_document
from exactly_lib.test_case_utils.parse.parse_path import parse_path_from_token_parser
from exactly_lib.test_case_utils.parse.parse_string import parse_string_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_utils.program.parse import parse_program
from exactly_lib.test_case_utils.string_transformer.impl import identity
from exactly_lib.test_case_utils.string_transformer.parse_string_transformer import parse_optional_transformer_sdv
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import is_option_string
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

CONTENTS_ASSIGNMENT_TOKEN = instruction_arguments.ASSIGNMENT_OPERATOR

PROGRAM_OUTPUT_OPTIONS = {
    ProcOutputFile.STDOUT: a.OptionName('stdout-from'),
    ProcOutputFile.STDERR: a.OptionName('stderr-from'),
}

FILE_OPTION = a.OptionName('file')
CONTENTS_ARGUMENT = 'CONTENTS'
_SRC_PATH_ARGUMENT = a.Named('SOURCE-FILE-PATH')


class FileContentsDocumentation:
    def __init__(self,
                 phase_is_after_act: bool,
                 contents_argument_sed: str):
        self._contents_argument_sed = contents_argument_sed
        self._src_rel_opt_arg_conf = _src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        self._tp = TextParser({
            'HERE_DOCUMENT': syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.singular_name,
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'program_type': types.PROGRAM_TYPE_INFO.name,
            'TRANSFORMATION': string_transformer.STRING_TRANSFORMATION_ARGUMENT.name,
            'transformer': syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
            'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
            'SRC_PATH_ARGUMENT': _SRC_PATH_ARGUMENT.name,
        })

    def syntax_element_descriptions(self) -> list:
        return [
            self._file_contents_sed(),
            rel_path_doc.path_element_2(self._src_rel_opt_arg_conf,
                                        docs.paras(the_path_of('an existing file.'))),
            self._transformation_sed(),
        ]

    def see_also_targets(self) -> list:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT,
                               syntax_elements.STRING_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT,
                               syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
                               syntax_elements.PROGRAM_SYNTAX_ELEMENT,
                               ]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    def _file_contents_sed(self) -> SyntaxElementDescription:
        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  string_transformer.STRING_TRANSFORMATION_ARGUMENT)

        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)

        string_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.STRING)

        program_token = a.Single(a.Multiplicity.MANDATORY,
                                 syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument)

        output_channel_token = a.Choice(a.Multiplicity.MANDATORY,
                                        [a.Option(option_name) for option_name in PROGRAM_OUTPUT_OPTIONS.values()])

        file_option = a.Single(a.Multiplicity.MANDATORY,
                               a.Option(FILE_OPTION))

        src_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                _SRC_PATH_ARGUMENT)

        invokation_variants = [
            invokation_variant_from_args([string_arg]),
            invokation_variant_from_args([here_doc_arg]),
            invokation_variant_from_args([file_option,
                                          src_file_arg,
                                          optional_transformation_option,
                                          ],
                                         self._tp.fnap(_FILE_DESCRIPTION)),
            invokation_variant_from_args([output_channel_token,
                                          program_token],
                                         self._tp.fnap(_PROGRAM_DESCRIPTION)),
        ]
        return SyntaxElementDescription(self._contents_argument_sed,
                                        [],
                                        invokation_variants)

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            string_transformer.STRING_TRANSFORMATION_ARGUMENT,
            self._tp.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       string_transformer.TRANSFORMATION_OPTION)]),
            ]
        )


class InstructionConfig:
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 src_rel_opt_arg_conf: RelOptionArgumentConfiguration,
                 syntax_element: str):
        self.source_info = source_info
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
        parser.consume_mandatory_constant_unquoted_string(CONTENTS_ASSIGNMENT_TOKEN, True)
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
            contents = parse_here_document.parse_as_last_argument_from_token_parser(True, parser)
            return FileMakerForConstantContents(contents)
        else:
            contents = parse_string_from_token_parser(parser)
            parser.report_superfluous_arguments_if_not_at_eol()
            return FileMakerForConstantContents(contents)


def _parse_file_maker_with_transformation(instruction_config: InstructionConfig,
                                          parser: TokenParser) -> FileMaker:
    def _parse_program_from_stdout(my_parser: TokenParser) -> FileMaker:
        program = parse_program.parse_program(my_parser)
        return FileMakerForContentsFromProgram(instruction_config.source_info,
                                               ProcOutputFile.STDOUT,
                                               program)

    def _parse_program_from_stderr(my_parser: TokenParser) -> FileMaker:
        program = parse_program.parse_program(my_parser)
        return FileMakerForContentsFromProgram(instruction_config.source_info,
                                               ProcOutputFile.STDERR,
                                               program)

    def _parse_file(my_parser: TokenParser) -> FileMaker:
        src_file = parse_path_from_token_parser(instruction_config.src_rel_opt_arg_conf,
                                                my_parser)
        contents_transformer = parse_optional_transformer_sdv(parser)
        my_parser.report_superfluous_arguments_if_not_at_eol()
        return FileMakerForContentsFromExistingFile(instruction_config.source_info,
                                                    identity.IDENTITY_TRANSFORMER_SDV
                                                    if contents_transformer is None
                                                    else
                                                    contents_transformer,
                                                    src_file)

    return parser.parse_mandatory_option({
        PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDOUT]: _parse_program_from_stdout,
        PROGRAM_OUTPUT_OPTIONS[ProcOutputFile.STDERR]: _parse_program_from_stderr,
        FILE_OPTION: _parse_file,
    })


def _src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool) -> RelOptionArgumentConfiguration:
    rel_option_types = _SRC_REL_OPTIONS__AFTER_ACT if phase_is_after_act else _SRC_REL_OPTIONS__BEFORE_ACT
    return _src_rel_opt_arg_conf(rel_option_types)


def _src_rel_opt_arg_conf(rel_option_types: set) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(PathRelativityVariants(
            rel_option_types,
            True),
            RelOptionType.REL_CWD),
        _SRC_PATH_ARGUMENT.name,
        True)


_SRC_REL_OPTIONS__BEFORE_ACT = set(RelOptionType).difference({RelOptionType.REL_RESULT})
_SRC_REL_OPTIONS__AFTER_ACT = set(RelOptionType)

_TRANSFORMATION_DESCRIPTION = """\
Transforms the original contents.
"""

_PROGRAM_DESCRIPTION = """\
The output from {program_type:a/q}.


{PROGRAM} includes arguments until end of line,
and an optional {TRANSFORMATION} on a following line.


The {program_type} must terminate.
"""

_FILE_DESCRIPTION = """\
The contents of an existing file.


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the file {SRC_PATH_ARGUMENT} is NOT substituted.
"""
