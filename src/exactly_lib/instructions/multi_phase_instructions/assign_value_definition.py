from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case.file_ref_relativity import RelOptionType
from exactly_lib.test_case.value_definition import ValueDefinitionOfPath
from exactly_lib.value_definition.symbol_table_contents import FileRefValue


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, additional_format_map: dict = None, is_in_assert_phase: bool = False):
        super().__init__(name, additional_format_map, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Assigns a path value to a name')

    def _main_description_rest_body(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return [
        ]

    def syntax_element_descriptions(self) -> list:
        return [
        ]

    def _see_also_cross_refs(self) -> list:
        concepts = rel_path_doc.see_also_concepts(REL_OPTIONS_CONFIGURATION.accepted_options)
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


def parse(source: ParseSource) -> ValueDefinitionOfPath:
    source_line = source.current_line
    token_stream = TokenStream2(source.remaining_part_of_current_line)
    source.consume_current_line()
    if token_stream.is_null:
        raise SingleInstructionInvalidArgumentException('Missing value name')
    name_token = token_stream.head
    if name_token.is_quoted:
        raise SingleInstructionInvalidArgumentException('Name cannot be quoted: ' + name_token.source_string)
    name_str = name_token.string
    token_stream.consume()
    if token_stream.is_null or token_stream.head.source_string != '=':
        raise SingleInstructionInvalidArgumentException('Missing =')
    token_stream.consume()
    file_ref = parse_file_ref.parse_file_ref(token_stream, REL_OPTION_ARGUMENT_CONFIGURATION)
    if not token_stream.is_null:
        msg = 'Superfluous arguments: ' + token_stream.remaining_part_of_current_line
        raise SingleInstructionInvalidArgumentException(msg)
    return ValueDefinitionOfPath(name_str, FileRefValue(source_line, file_ref))


REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(parse_file_ref.ALL_REL_OPTION_VARIANTS,
                                                    True,
                                                    RelOptionType.REL_CWD)

REL_OPTION_ARGUMENT_CONFIGURATION = RelOptionArgumentConfiguration(REL_OPTIONS_CONFIGURATION,
                                                                   dt.PATH_ARGUMENT)
