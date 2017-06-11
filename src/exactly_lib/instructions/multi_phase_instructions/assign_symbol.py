from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.concepts.names_and_cross_references import CURRENT_WORKING_DIRECTORY_CONCEPT_INFO, \
    SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.argument_rendering import path_syntax
from exactly_lib.help_texts.test_case.instructions import assign_symbol as syntax_elements
from exactly_lib.instructions.utils.arg_parse import parse_file_ref
from exactly_lib.instructions.utils.arg_parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.instructions.utils.arg_parse.symbol import is_symbol_name
from exactly_lib.instructions.utils.documentation import documentation_text as dt
from exactly_lib.instructions.utils.documentation import relative_path_options_documentation as rel_path_doc
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.symbol.value_resolvers.string_resolvers import StringConstant
from exactly_lib.symbol.value_structure import SymbolDefinition, ValueContainer, SymbolValueResolver
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        self.name = a.Named('NAME')
        self.string_value = a.Named('STRING')
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
        return [
            InvokationVariant(syntax_elements.definition_of_type_string()),
            InvokationVariant(syntax_elements.definition_of_type_path()),
        ]

    def syntax_element_descriptions(self) -> list:
        return rel_path_doc.relativity_syntax_element_descriptions(
            _PATH_ARGUMENT,
            REL_OPTION_ARGUMENT_CONFIGURATION.options) + \
               [
                   SyntaxElementDescription(self.string_value.name,
                                            self._paragraphs(_STRING_SYNTAX_ELEMENT_DESCRIPTION)),
               ]

    def _see_also_cross_refs(self) -> list:
        concepts = []
        concepts.append(SYMBOL_CONCEPT_INFO)
        concepts.extend(rel_path_doc.see_also_concepts(REL_OPTIONS_CONFIGURATION))
        rel_path_doc.add_concepts_if_not_listed(concepts, [CURRENT_WORKING_DIRECTORY_CONCEPT_INFO])
        return [concept.cross_reference_target for concept in concepts]


def parse(source: ParseSource) -> SymbolDefinition:
    source_line = source.current_line
    token_stream = TokenStream2(source.remaining_part_of_current_line)
    source.consume_current_line()
    if token_stream.is_null:
        err_msg = 'Missing symbol type.\nExpecting one of ' + _TYPES_LIST_IN_ERR_MSG
        raise SingleInstructionInvalidArgumentException(err_msg)
    type_token = token_stream.head
    if type_token.source_string not in _TYPE_SETUPS:
        err_msg = 'Invalid type :{}\nExpecting one of {}'.format(type_token.source_string, _TYPES_LIST_IN_ERR_MSG)
        raise SingleInstructionInvalidArgumentException(err_msg)
    value_parser = _TYPE_SETUPS[type_token.source_string]
    token_stream.consume()
    if token_stream.is_null:
        err_msg = 'Missing symbol name.'
        raise SingleInstructionInvalidArgumentException(err_msg)
    name_token = token_stream.head
    if name_token.is_quoted:
        raise SingleInstructionInvalidArgumentException('Name cannot be quoted: ' + name_token.source_string)
    name_str = name_token.string
    if not is_symbol_name(name_str):
        err_msg = 'Invalid symbol name: {}.\nA symbol name must only contain alphanum and _'.format(name_str)
        raise SingleInstructionInvalidArgumentException(err_msg)
    token_stream.consume()
    if token_stream.is_null or token_stream.head.source_string != syntax_elements.EQUALS_ARGUMENT:
        raise SingleInstructionInvalidArgumentException('Missing ' + syntax_elements.EQUALS_ARGUMENT)
    token_stream.consume()
    value = value_parser(token_stream)
    if not token_stream.is_null:
        msg = 'Superfluous arguments: ' + token_stream.remaining_part_of_current_line
        raise SingleInstructionInvalidArgumentException(msg)
    return SymbolDefinition(name_str, ValueContainer(source_line, value))


_PATH_ARGUMENT = path_syntax.PATH_ARGUMENT

REL_OPTIONS_CONFIGURATION = RelOptionsConfiguration(
    PathRelativityVariants(frozenset(RelOptionType), True),
    True,
    RelOptionType.REL_CWD)

REL_OPTION_ARGUMENT_CONFIGURATION = RelOptionArgumentConfiguration(REL_OPTIONS_CONFIGURATION,
                                                                   path_syntax.PATH_ARGUMENT,
                                                                   syntax_elements.PATH_SUFFIX_IS_REQUIRED)

_MAIN_DESCRIPTION_REST = """\
Defines the symbol {NAME} to be the given string or path.


{NAME} must not have been defined earlier.
"""

_STRING_SYNTAX_ELEMENT_DESCRIPTION = """\
A single word, or a single quoted text.
"""


def _parse_path(token_stream: TokenStream2) -> SymbolValueResolver:
    return parse_file_ref.parse_file_ref(token_stream, REL_OPTION_ARGUMENT_CONFIGURATION)


def _parse_string(token_stream: TokenStream2) -> SymbolValueResolver:
    if token_stream.is_null:
        raise SingleInstructionInvalidArgumentException('Missing {} value'.format(syntax_elements.STRING_TYPE))
    ret_val = StringConstant(token_stream.head.string)
    token_stream.consume()
    return ret_val


_TYPE_SETUPS = {
    syntax_elements.PATH_TYPE: _parse_path,
    syntax_elements.STRING_TYPE: _parse_string,
}

_TYPES_LIST_IN_ERR_MSG = '|'.join(sorted(_TYPE_SETUPS.keys()))
