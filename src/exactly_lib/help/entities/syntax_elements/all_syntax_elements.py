from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import for_type_with_grammar
from exactly_lib.help.entities.syntax_elements.objects import here_document, regex, glob_pattern, \
    type_string, type_list, type_path, type_program, symbol_name, symbol_reference, \
    integer, integer_comparison, shell_command_line
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_condition import parse as parse_files_condition
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer

ALL_SYNTAX_ELEMENT_DOCS = (

    integer.DOCUMENTATION,
    integer_comparison.DOCUMENTATION,

    here_document.DOCUMENTATION,
    regex.DOCUMENTATION,
    glob_pattern.DOCUMENTATION,
    shell_command_line.DOCUMENTATION,
    symbol_name.DOCUMENTATION,
    symbol_reference.DOCUMENTATION,

    type_string.DOCUMENTATION,
    type_list.DOCUMENTATION,
    type_path.DOCUMENTATION,

    for_type_with_grammar(syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
                          parse_file_matcher.GRAMMAR),

    for_type_with_grammar(syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
                          parse_files_matcher.GRAMMAR),

    for_type_with_grammar(syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
                          parse_string_matcher.GRAMMAR),

    for_type_with_grammar(syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
                          parse_line_matcher.GRAMMAR),

    for_type_with_grammar(syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
                          parse_string_transformer.GRAMMAR),

    for_type_with_grammar(syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT,
                          parse_files_condition.GRAMMAR),

    type_program.DOCUMENTATION,

)

NAME_2_SYNTAX_ELEMENT_DOC = dict(map(lambda x: (x.singular_name(), x), ALL_SYNTAX_ELEMENT_DOCS))
