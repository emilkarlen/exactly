from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation, \
    syntax_element_documentation
from exactly_lib.help.entities.syntax_elements.objects import here_document, regex, glob_pattern, \
    type_string, type_list, type_path, symbol_name, symbol_reference, file_contents_matcher, \
    integer, integer_comparison
from exactly_lib.help_texts.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help_texts.entity import syntax_elements
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.test_case_utils.expression.syntax_documentation import Syntax
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.type_system.value_type import TypeCategory


def _for_logic_type(type_info: SingularNameAndCrossReferenceId,
                    grammar: Grammar) -> SyntaxElementDocumentation:
    syntax = Syntax(grammar)
    return syntax_element_documentation(TypeCategory.LOGIC,
                                        type_info,
                                        syntax.global_description(),
                                        syntax.invokation_variants(),
                                        [],
                                        syntax.see_also_targets())


ALL_SYNTAX_ELEMENT_DOCS = (

    integer.DOCUMENTATION,
    integer_comparison.DOCUMENTATION,

    here_document.DOCUMENTATION,
    regex.DOCUMENTATION,
    glob_pattern.DOCUMENTATION,
    symbol_name.DOCUMENTATION,
    symbol_reference.DOCUMENTATION,
    file_contents_matcher.DOCUMENTATION,

    type_string.DOCUMENTATION,
    type_list.DOCUMENTATION,
    type_path.DOCUMENTATION,

    _for_logic_type(syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
                    parse_file_matcher.GRAMMAR),

    _for_logic_type(syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT,
                    parse_lines_transformer.GRAMMAR),

    _for_logic_type(syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
                    parse_line_matcher.GRAMMAR),
)

NAME_2_SYNTAX_ELEMENT_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_SYNTAX_ELEMENT_DOCS))
