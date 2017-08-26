import pathlib

import exactly_lib.test_case_utils.parse.parse_file_transformer
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import parsing
from exactly_lib.instructions.assert_.utils.file_contents.contents_utils_for_instr_doc import FileContentsHelpParts
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer.env_vars_replacement_transformer import \
    FileTransformerForEnvVarsReplacement, PathResolverForEnvVarReplacement
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.test_case_utils.parse.parse_file_transformer import FileTransformerParser
from exactly_lib.util.cli_syntax.elements import argument as a


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
        self.with_replaced_env_vars_option = a.Option(
            exactly_lib.test_case_utils.parse.parse_file_transformer.WITH_REPLACED_ENV_VARS_OPTION_NAME)

    def single_line_description(self) -> str:
        return self._format('Tests the contents of {checked_file}')

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

    def syntax_element_descriptions(self) -> list:
        return (self._help_parts.syntax_element_descriptions_at_top() +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_items(self) -> list:
        return self._help_parts.see_also_items()


_WITH_REPLACED_ENV_VARS_STEM_SUFFIX = '-with-replaced-env-vars.txt'


class ParserForContentsForActualValue(InstructionParser):
    def __init__(self,
                 comparison_actual_value: actual_files.ComparisonActualFile):
        self.comparison_actual_value = comparison_actual_value

    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        source.consume_initial_space_on_current_line()
        first_line = source.remaining_part_of_current_line
        content_instruction = parsing.parse_comparison_operation(self.comparison_actual_value,
                                                                 FileTransformerParser(
                                                                     _PathResolverForEnvVarReplacement()),
                                                                 source)
        if content_instruction is None:
            raise SingleInstructionInvalidArgumentException(first_line)
        return content_instruction


class _PathResolverForEnvVarReplacement(PathResolverForEnvVarReplacement):
    def dst_file_path(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      src_file_path: pathlib.Path) -> pathlib.Path:
        src_stem_name = src_file_path.stem
        directory = src_file_path.parent
        dst_base_name = src_stem_name + _WITH_REPLACED_ENV_VARS_STEM_SUFFIX
        return pathlib.Path(directory / dst_base_name)


def actual_file_transformer_for_env_vars_replacement() -> FileTransformerForEnvVarsReplacement:
    return FileTransformerForEnvVarsReplacement(_PathResolverForEnvVarReplacement())
