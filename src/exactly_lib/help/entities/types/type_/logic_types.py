from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation
from exactly_lib.help_texts.entity import types
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer

LINE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(types.LINE_MATCHER_CONCEPT_INFO,
                                                                         parse_line_matcher.GRAMMAR)

FILE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(types.FILE_MATCHER_CONCEPT_INFO,
                                                                         parse_file_matcher.GRAMMAR)

LINES_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(types.LINES_TRANSFORMER_CONCEPT_INFO,
                                                                              parse_lines_transformer.GRAMMAR)
