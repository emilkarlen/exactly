from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.entities.syntax_elements.element import here_document, regex, glob_pattern, \
    type_string, type_list, type_path
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.test_case_utils.expression.syntax_documentation import Syntax
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer


def _for_expression_grammar(type_info: SingularNameAndCrossReferenceId,
                            grammar: Grammar) -> SyntaxElementDocumentation:
    syntax = Syntax(grammar)
    return SyntaxElementDocumentation(type_info,
                                      [],
                                      syntax.invokation_variants(),
                                      syntax.see_also_targets())


ALL_SYNTAX_ELEMENT_DOCS = [

    here_document.DOCUMENTATION,
    regex.DOCUMENTATION,
    glob_pattern.DOCUMENTATION,

    type_string.DOCUMENTATION,
    type_list.DOCUMENTATION,
    type_path.DOCUMENTATION,

    _for_expression_grammar(syntax_element.FILE_MATCHER_SYNTAX_ELEMENT,
                            parse_file_matcher.GRAMMAR),

    _for_expression_grammar(syntax_element.LINES_TRANSFORMER_SYNTAX_ELEMENT,
                            parse_lines_transformer.GRAMMAR),

    _for_expression_grammar(syntax_element.LINE_MATCHER_SYNTAX_ELEMENT,
                            parse_line_matcher.GRAMMAR),
]

NAME_2_SYNTAX_ELEMENT_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_SYNTAX_ELEMENT_DOCS))
