from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args, \
    cli_argument_syntax_element_description
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref import name_and_cross_ref
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.file_maker import FileMaker, FileMakerForConstantContents, \
    FileMakerForContentsFromSubProcess, FileMakerForContentsFromExistingFile
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.test_case.phases.common import InstructionSourceInfo
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_utils.lines_transformer.parse_lines_transformer import parse_optional_transformer_resolver
from exactly_lib.test_case_utils.parse import parse_here_document
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_token_parser
from exactly_lib.test_case_utils.parse.parse_string import parse_string_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.test_case_utils.sub_proc.execution_setup import SubProcessExecutionSetup
from exactly_lib.test_case_utils.sub_proc.shell_program import ShellCommandSetupParser
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import is_option_string
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

CONTENTS_ASSIGNMENT_TOKEN = instruction_arguments.ASSIGNMENT_OPERATOR
SHELL_COMMAND_TOKEN = instruction_names.SHELL_INSTRUCTION_NAME
STDOUT_OPTION = a.OptionName(long_name='stdout')
FILE_OPTION = a.OptionName(long_name='file')
CONTENTS_ARGUMENT = 'CONTENTS'
_SRC_PATH_ARGUMENT = a.Named('SOURCE-FILE-PATH')


class FileContentsDocumentation:
    def __init__(self,
                 phase_is_after_act: bool,
                 contents_argument_sed: str):
        self._contents_argument_sed = contents_argument_sed
        self._src_rel_opt_arg_conf = _src_rel_opt_arg_conf_for_phase(phase_is_after_act)
        self._tp = TextParser({
            'HERE_DOCUMENT': syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.argument.name,
            'SHELL_COMMAND_LINE': instruction_arguments.COMMAND_ARGUMENT.name,
            'transformer': syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT.singular_name,
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
                               syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)

    def _file_contents_sed(self) -> SyntaxElementDescription:
        optional_transformation_option = a.Single(a.Multiplicity.OPTIONAL,
                                                  instruction_arguments.LINES_TRANSFORMATION_ARGUMENT)

        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)

        string_arg = a.Single(a.Multiplicity.MANDATORY,
                              instruction_arguments.STRING)

        shell_command_token = a.Single(a.Multiplicity.MANDATORY,
                                       a.Named(SHELL_COMMAND_TOKEN))

        command_arg = a.Single(a.Multiplicity.MANDATORY,
                               instruction_arguments.COMMAND_ARGUMENT)

        stdout_option = a.Single(a.Multiplicity.MANDATORY,
                                 a.Option(STDOUT_OPTION))

        file_option = a.Single(a.Multiplicity.MANDATORY,
                               a.Option(FILE_OPTION))

        src_file_arg = a.Single(a.Multiplicity.MANDATORY,
                                _SRC_PATH_ARGUMENT)

        invokation_variants = [
            invokation_variant_from_args([string_arg]),
            invokation_variant_from_args([here_doc_arg]),
            invokation_variant_from_args([optional_transformation_option,
                                          file_option,
                                          src_file_arg],
                                         self._tp.fnap(_FILE_DESCRIPTION)),
            invokation_variant_from_args([optional_transformation_option,
                                          stdout_option,
                                          shell_command_token,
                                          command_arg],
                                         self._tp.fnap(_SHELL_COMMAND_DESCRIPTION)),
        ]
        return SyntaxElementDescription(self._contents_argument_sed,
                                        [],
                                        invokation_variants)

    def _transformation_sed(self) -> SyntaxElementDescription:
        return cli_argument_syntax_element_description(
            instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
            self._tp.fnap(_TRANSFORMATION_DESCRIPTION),
            [
                invokation_variant_from_args([a.Single(a.Multiplicity.MANDATORY,
                                                       instruction_arguments.TRANSFORMATION_OPTION)]),
            ]
        )


class InstructionConfig:
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 src_rel_opt_arg_conf: RelOptionArgumentConfiguration):
        self.source_info = source_info
        self.src_rel_opt_arg_conf = src_rel_opt_arg_conf


def parse_file_contents(instruction_config: InstructionConfig,
                        parser: TokenParser) -> FileMaker:
    """
    Parses a file contents specification of the form: [= FILE-MAKER]

    :raises SingleInstructionInvalidArgumentException: Invalid arguments
    """
    if parser.is_at_eol:
        return FileMakerForConstantContents(string_resolver.string_constant(''))
    else:
        parser.consume_mandatory_constant_unquoted_string(CONTENTS_ASSIGNMENT_TOKEN, True)
        parser.require_is_not_at_eol('Missing ' + CONTENTS_ARGUMENT)

        return parse_file_maker(instruction_config, parser)


def parse_file_maker(instruction_config: InstructionConfig,
                     parser: TokenParser) -> FileMaker:
    parser.require_head_token_has_valid_syntax()

    head_source_string = parser.token_stream.head.source_string
    if is_option_string(head_source_string):
        contents_transformer = parse_optional_transformer_resolver(parser)
        return _parse_file_maker_with_transformation(instruction_config,
                                                     parser,
                                                     contents_transformer)
    else:
        if head_source_string.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
            contents = parse_here_document.parse_as_last_argument_from_token_parser(True, parser)
            return FileMakerForConstantContents(contents)
        else:
            contents = parse_string_from_token_parser(parser)
            parser.report_superfluous_arguments_if_not_at_eol()
            return FileMakerForConstantContents(contents)


def _parse_file_maker_with_transformation(instruction_config: InstructionConfig,
                                          parser: TokenParser,
                                          contents_transformer: LinesTransformerResolver) -> FileMaker:
    def parse_sub_process(my_parser: TokenParser) -> FileMaker:
        sub_process = _parse_sub_process_setup(my_parser)
        return FileMakerForContentsFromSubProcess(instruction_config.source_info,
                                                  contents_transformer,
                                                  sub_process)

    def parse_file(my_parser: TokenParser) -> FileMaker:
        src_file = parse_file_ref_from_token_parser(instruction_config.src_rel_opt_arg_conf,
                                                    my_parser)
        my_parser.report_superfluous_arguments_if_not_at_eol()
        return FileMakerForContentsFromExistingFile(instruction_config.source_info,
                                                    contents_transformer,
                                                    src_file)

    return parser.parse_mandatory_option({
        STDOUT_OPTION: parse_sub_process,
        FILE_OPTION: parse_file,
    })


def _parse_sub_process_setup(parser: TokenParser) -> SubProcessExecutionSetup:
    parser.consume_mandatory_constant_unquoted_string(SHELL_COMMAND_TOKEN, False)
    setup_parser = ShellCommandSetupParser()
    return setup_parser.parse_from_token_parser(parser)


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
_SHELL_COMMAND_DESCRIPTION = """\
The output from a shell command.


{SHELL_COMMAND_LINE} is the literal text until end of line.
"""
_FILE_DESCRIPTION = """\
The contents of an existing file.
"""
