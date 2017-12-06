import pathlib

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.argument_rendering.path_syntax import the_path_of
from exactly_lib.help_texts.cross_ref import name_and_cross_ref
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.multi_phase_instructions.utils import file_creation
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForErrorMessageStringResultAsHardError
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionPartsParser
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import from_parse_source, \
    TokenParserPrime
from exactly_lib.symbol.data import string_resolver
from exactly_lib.symbol.data.path_resolver import FileRefResolver
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths, \
    InstructionSourceInfo, instruction_log_dir
from exactly_lib.test_case_utils.parse import parse_here_document
from exactly_lib.test_case_utils.parse.parse_file_ref import parse_file_ref_from_token_parser
from exactly_lib.test_case_utils.parse.rel_opts_configuration import argument_configuration_for_file_creation, \
    RELATIVITY_VARIANTS_FOR_FILE_CREATION
from exactly_lib.test_case_utils.sub_proc.execution_setup import SubProcessExecutionSetup
from exactly_lib.test_case_utils.sub_proc.shell_program import ShellCommandSetupParser
from exactly_lib.test_case_utils.sub_proc.sub_process_execution import ExecutorThatStoresResultInFilesInDir, \
    execute_and_read_stderr_if_non_zero_exitcode
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser

CONTENTS_ASSIGNMENT_TOKEN = '='
SHELL_COMMAND_TOKEN = instruction_names.SHELL_INSTRUCTION_NAME

CONTENTS_ARGUMENT = 'CONTENTS'


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str):
        super().__init__(name, {})

        self._tp = TextParser({
            'HERE_DOCUMENT': syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT.argument.name
        })

    def single_line_description(self) -> str:
        return 'Creates a file'

    def invokation_variants(self) -> list:
        arguments = path_syntax.mandatory_path_with_optional_relativity(
            _PATH_ARGUMENT,
            REL_OPT_ARG_CONF.path_suffix_is_required)
        here_doc_arg = a.Single(a.Multiplicity.MANDATORY,
                                instruction_arguments.HERE_DOCUMENT)
        assignment_arg = a.Single(a.Multiplicity.MANDATORY,
                                  a.Constant(CONTENTS_ASSIGNMENT_TOKEN))
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments),
                              docs.paras('Creates an empty file.')),
            InvokationVariant(self._cl_syntax_for_args(arguments + [assignment_arg, here_doc_arg]),
                              self._tp.paras('Creates a file with contents given by a {HERE_DOCUMENT}.')),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_path_doc.path_element(_PATH_ARGUMENT.name,
                                      REL_OPT_ARG_CONF.options,
                                      docs.paras(the_path_of('a non-existing file.')))
        ]

    def see_also_targets(self) -> list:
        name_and_cross_refs = [syntax_elements.PATH_SYNTAX_ELEMENT,
                               syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT]
        return name_and_cross_ref.cross_reference_id_list(name_and_cross_refs)


class InstructionEmbryoForConstantContents(embryo.InstructionEmbryo):
    def __init__(self,
                 path_to_create: FileRefResolver,
                 contents: string_resolver.StringResolver):
        self._path_to_create = path_to_create
        self._contents = contents

    @property
    def symbol_usages(self) -> list:
        return self._path_to_create.references + self._contents.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> str:
        path_to_create = self._path_to_create.resolve(environment.symbols).value_post_sds(environment.sds)
        contents_str = self._contents.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)
        return create_file(path_to_create, contents_str)


class InstructionEmbryoForContentsFromSubProcess(embryo.InstructionEmbryo):
    def __init__(self,
                 source_info: InstructionSourceInfo,
                 path_to_create: FileRefResolver,
                 sub_process: SubProcessExecutionSetup):
        self._source_info = source_info
        self._path_to_create = path_to_create
        self._sub_process = sub_process

    @property
    def symbol_usages(self) -> list:
        return self._path_to_create.references + self._sub_process.symbol_usages

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices) -> str:
        executor = ExecutorThatStoresResultInFilesInDir(environment.process_execution_settings)
        command = self._sub_process.resolve_command(environment.path_resolving_environment_pre_or_post_sds)
        storage_dir = instruction_log_dir(logging_paths, self._source_info)

        result_and_std_err = execute_and_read_stderr_if_non_zero_exitcode(command, executor, storage_dir)

        if not result_and_std_err.result.is_success:
            return result_and_std_err.stderr_contents

        path_to_create = self._path_to_create.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)

        path_to_copy = storage_dir / result_and_std_err.result.file_names.stdout

        os_services.copy_file_preserve_as_much_as_possible__detect_ex(
            str(path_to_copy),
            str(path_to_create))
        return None


class EmbryoParser(embryo.InstructionEmbryoParser):
    def __init__(self, instruction_name: str):
        self._instruction_name = instruction_name

    def parse(self, source: ParseSource) -> embryo.InstructionEmbryo:
        first_line_number = source.current_line_number
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            assert isinstance(parser, TokenParserPrime)  # Type info for IDE
            file_ref = parse_file_ref_from_token_parser(REL_OPT_ARG_CONF, parser)
            if not parser.is_at_eol:
                parser.consume_mandatory_constant_unquoted_string(CONTENTS_ASSIGNMENT_TOKEN, True)
                parser.require_is_not_at_eol('Missing ' + CONTENTS_ARGUMENT)

                parser.require_head_token_has_valid_syntax()

                if parser.token_stream.head.source_string.startswith(parse_here_document.DOCUMENT_MARKER_PREFIX):
                    contents = parse_here_document.parse_as_last_argument_from_token_parser(True, parser)
                    return InstructionEmbryoForConstantContents(file_ref, contents)
                else:
                    sub_process = self._parse_sub_process_setup(parser)
                    source_info = InstructionSourceInfo(first_line_number,
                                                        self._instruction_name)
                    return InstructionEmbryoForContentsFromSubProcess(source_info, file_ref, sub_process)
            else:
                return InstructionEmbryoForConstantContents(file_ref, string_resolver.string_constant(''))

    def _parse_sub_process_setup(self, parser: TokenParserPrime) -> SubProcessExecutionSetup:
        parser.consume_mandatory_constant_unquoted_string(SHELL_COMMAND_TOKEN, True)
        setup_parser = ShellCommandSetupParser()
        return setup_parser.parse_from_token_parser(parser)


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return PartsParserFromEmbryoParser(EmbryoParser(instruction_name),
                                       MainStepResultTranslatorForErrorMessageStringResultAsHardError())


def create_file(path_to_create: pathlib.Path,
                contents_str: str) -> str:
    """
    :return: None iff success. Otherwise an error message.
    """

    def write_file(f):
        f.write(contents_str)

    return file_creation.create_file(path_to_create,
                                     write_file)


_PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

RELATIVITY_VARIANTS = RELATIVITY_VARIANTS_FOR_FILE_CREATION

REL_OPT_ARG_CONF = argument_configuration_for_file_creation(_PATH_ARGUMENT.name)
