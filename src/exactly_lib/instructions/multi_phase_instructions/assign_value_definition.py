from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO, \
    SYMBOL_CONCEPT_INFO
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.destination_paths import *
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.value_definition.concrete_values import FileRefValue
from exactly_lib.value_definition.value_structure import ValueDefinition, ValueContainer


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        self.name = a.Named('NAME')
        super().__init__(name, {
            'NAME': self.name.name,
        }, is_in_assert_phase)

    def single_line_description(self) -> str:
        return self._format('Defines a symbol that can be used by later instructions')

    def _main_description_rest_body(self) -> list:
        return (
            self._parser.fnap(_MAIN_DESCRIPTION_REST) +
            rel_path_doc.default_relativity_for_rel_opt_type(
                _PATH_ARGUMENT.name,
                REL_OPTION_ARGUMENT_CONFIGURATION.options.default_option) +
            dt.paths_uses_posix_syntax())

    def invokation_variants(self) -> list:
        arguments = [
            a.Single(a.Multiplicity.MANDATORY, self.name),
            a.Single(a.Multiplicity.MANDATORY, a.Constant(_EQUALS_ARGUMENT)),
        ]
        arguments.extend(rel_path_doc.mandatory_path_with_optional_relativity(_PATH_ARGUMENT))
        return [
            InvokationVariant(self._cl_syntax_for_args(arguments)),
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            rel_path_doc.relativity_syntax_element_description(
                _PATH_ARGUMENT,
                REL_OPTION_ARGUMENT_CONFIGURATION.options),
        ]

    def _see_also_cross_refs(self) -> list:
        concepts = []
        concepts.append(SYMBOL_CONCEPT_INFO)
        concepts.extend(rel_path_doc.see_also_concepts(REL_OPTIONS_CONFIGURATION))
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


def parse(source: ParseSource) -> ValueDefinition:
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
    if token_stream.is_null or token_stream.head.source_string != _EQUALS_ARGUMENT:
        raise SingleInstructionInvalidArgumentException('Missing ' + _EQUALS_ARGUMENT)
    token_stream.consume()
    file_ref = parse_file_ref.parse_file_ref(token_stream, REL_OPTION_ARGUMENT_CONFIGURATION)
    if not token_stream.is_null:
        msg = 'Superfluous arguments: ' + token_stream.remaining_part_of_current_line
        raise SingleInstructionInvalidArgumentException(msg)
    return ValueDefinition(name_str, ValueContainer(source_line, FileRefValue(file_ref)))


_EQUALS_ARGUMENT = '='

_PATH_ARGUMENT = dt.PATH_ARGUMENT

REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(
    PathRelativityVariants(frozenset(RelOptionType), True),
    True,
    RelOptionType.REL_CWD)

REL_OPTION_ARGUMENT_CONFIGURATION = RelOptionArgumentConfiguration(REL_OPTIONS_CONFIGURATION,
                                                                   dt.PATH_ARGUMENT)

_MAIN_DESCRIPTION_REST = """\
Defines the symbol {NAME} to be the given path.


{NAME} must not have been defined earlier.
"""
