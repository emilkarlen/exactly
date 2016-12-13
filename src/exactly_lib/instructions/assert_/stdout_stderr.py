import pathlib

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.assert_.utils.file_contents.actual_file_transformers import \
    ActualFileTransformerForEnvVarsReplacementBase, \
    ActualFileTransformer
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.instructions.utils.arg_parse import parse_here_doc_or_file_ref
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.cli_syntax.elements import argument as a


def setup_for_stdout(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        ParserForContentsForStdout(),
        TheInstructionDocumentation(instruction_name, 'stdout'))


def setup_for_stderr(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        ParserForContentsForStderr(),
        TheInstructionDocumentation(instruction_name, 'stderr'))


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase):
    def __init__(self, name: str,
                 name_of_checked_file: str):
        self.file_arg = a.Named(parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name)
        self._help_parts = FileContentsHelpParts(name,
                                                 name_of_checked_file,
                                                 [])

        super().__init__(name, {
            'checked_file': name_of_checked_file,
            'FILE_ARG': self.file_arg.name,
        })
        self.checked_file = name_of_checked_file
        self.with_replaced_env_vars_option = a.Option(parsing.WITH_REPLACED_ENV_VARS_OPTION_NAME)

    def single_line_description(self) -> str:
        return self._format('Tests the contents of {checked_file}')

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

    def syntax_element_descriptions(self) -> list:
        return self._help_parts.syntax_element_descriptions()

    def _see_also_cross_refs(self) -> list:
        return self._help_parts.see_also()


_WITH_REPLACED_ENV_VARS_STEM_SUFFIX = '-with-replaced-env-vars.txt'


class ParserForContentsForActualValue(SingleInstructionParser):
    def __init__(self,
                 comparison_actual_value: actual_files.ComparisonActualFile,
                 actual_value_transformer: ActualFileTransformer):
        self.comparison_actual_value = comparison_actual_value
        self.target_transformer = actual_value_transformer

    def apply(self, source: SingleInstructionParserSource) -> AssertPhaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        content_instruction = parsing.parse_comparison_operation(self.comparison_actual_value,
                                                                 self.target_transformer,
                                                                 arguments,
                                                                 source)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(str(arguments))
        return content_instruction


class ParserForContentsForStdout(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(actual_files.StdoutComparisonActualFile(),
                         _StdXActualFileTransformerForEnvVarsReplacementBase())


class ParserForContentsForStderr(ParserForContentsForActualValue):
    def __init__(self):
        super().__init__(actual_files.StderrComparisonActualFile(),
                         _StdXActualFileTransformerForEnvVarsReplacementBase())


class _StdXActualFileTransformerForEnvVarsReplacementBase(ActualFileTransformerForEnvVarsReplacementBase):
    def _dst_file_path(self,
                       environment: InstructionEnvironmentForPostSdsStep,
                       src_file_path: pathlib.Path) -> pathlib.Path:
        src_stem_name = src_file_path.stem
        directory = src_file_path.parent
        dst_base_name = src_stem_name + _WITH_REPLACED_ENV_VARS_STEM_SUFFIX
        return directory / dst_base_name
