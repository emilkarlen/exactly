from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation, \
    TypeDocumentation
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import empty_section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser

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

STRING_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.STRING_TRANSFORMER_TYPE_INFO,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
    parse_string_transformer.GRAMMAR,
    empty_section_contents())

_TEXT_PARSER = TextParser({
})

PROGRAM_DOCUMENTATION = TypeDocumentation(TypeCategory.LOGIC,
                                          types.PROGRAM_TYPE_INFO,
                                          syntax_elements.PROGRAM_SYNTAX_ELEMENT,
                                          docs.empty_section_contents())
