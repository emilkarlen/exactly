from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation
from exactly_lib.help_texts.entity import types, syntax_elements
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.util.textformat.structure.document import empty_section_contents

LINE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.LINE_MATCHER_TYPE_INFO,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
    parse_line_matcher.GRAMMAR,
    empty_section_contents())

FILE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILE_MATCHER_TYPE_INFO,
    syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
    parse_file_matcher.GRAMMAR,
    empty_section_contents())

LINES_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.LINES_TRANSFORMER_TYPE_INFO,
    syntax_elements.LINES_TRANSFORMER_SYNTAX_ELEMENT,
    parse_lines_transformer.GRAMMAR,
    empty_section_contents())
