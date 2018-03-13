from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithCommandLineRenderingBase
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents import parse_instruction
from exactly_lib.instructions.assert_.utils.file_contents.syntax.file_contents_checker import \
    FileContentsCheckerHelp
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
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


class ParserForContentsForActualValue(InstructionParser):
    def __init__(self,
                 comparison_actual_value: actual_files.ComparisonActualFile):
        self.comparison_actual_value = comparison_actual_value

    def parse(self, source: ParseSource) -> AssertPhaseInstruction:
        with from_parse_source(source, consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser, TokenParser), 'Must have a TokenParser'  # Type info for IDE
            return parse_instruction.parse_instruction(self.comparison_actual_value,
                                                       token_parser)
