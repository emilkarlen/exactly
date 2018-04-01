from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parse_instruction import ComparisonActualFileParser
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_checker import \
    FileContentsCheckerHelp
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import file_ref_resolvers2
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationWithCommandLineRenderingBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str,
                 name_of_checked_file: str):
        self.file_arg = a.Named(parse_here_doc_or_file_ref.CONFIGURATION.argument_syntax_name)
        self._help_parts = FileContentsCheckerHelp(name,
                                                   name_of_checked_file,
                                                   [])

        super().__init__(name, {
            'checked_file': name_of_checked_file,
            'FILE_ARG': self.file_arg.name,
        })
        self.checked_file = name_of_checked_file

    def single_line_description(self) -> str:
        return self._format('Tests the contents of {checked_file}')

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return self._help_parts.invokation_variants()

    def syntax_element_descriptions(self) -> list:
        return (self._help_parts.syntax_element_descriptions_at_top() +
                self._help_parts.syntax_element_descriptions_at_bottom())

    def see_also_targets(self) -> list:
        return self._help_parts.see_also_targets()


class Parser(ComparisonActualFileParser):
    def __init__(self, actual_value_if_not_output_from_program: actual_files.ComparisonActualFile):
        self._actual_value_if_not_output_from_program = actual_value_if_not_output_from_program

    def parse_from_token_parser(self, parser: TokenParser) -> ComparisonActualFile:
        return self._actual_value_if_not_output_from_program


class ActComparisonActualFileForStdFileBase(ComparisonActualFile):
    def __init__(self, checked_file_name: str):
        self.checked_file_name = checked_file_name

    def object_name(self) -> str:
        return self.checked_file_name

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return None

    def file_ref_resolver(self) -> FileRefResolver:
        return file_ref_resolvers2.of_rel_option(RelOptionType.REL_RESULT,
                                                 PathPartAsFixedPath(self.checked_file_name))