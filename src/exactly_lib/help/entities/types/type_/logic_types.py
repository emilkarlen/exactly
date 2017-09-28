from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.entity import types
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer

LINE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(type_system.LINE_MATCHER_TYPE,
                                                                         types.LINE_MATCHER_CONCEPT_INFO,
                                                                         parse_line_matcher.GRAMMAR)

FILE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(type_system.FILE_MATCHER_TYPE,
                                                                         types.FILE_MATCHER_CONCEPT_INFO,
                                                                         parse_file_matcher.GRAMMAR)

LINES_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(type_system.LINES_TRANSFORMER_TYPE,
                                                                              types.LINES_TRANSFORMER_CONCEPT_INFO,
                                                                              parse_lines_transformer.GRAMMAR)
