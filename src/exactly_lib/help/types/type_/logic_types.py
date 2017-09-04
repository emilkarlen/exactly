from exactly_lib.help.types.contents_structure import TypeWithExpressionGrammarDocumentation
from exactly_lib.help_texts import type_system
from exactly_lib.help_texts.entity import types
from exactly_lib.test_case_utils.file_selectors import parse_file_matcher
from exactly_lib.test_case_utils.lines_transformers import parse_lines_transformer

LINES_TRANSFORMER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(type_system.LINES_TRANSFORMER_TYPE,
                                                                         types.LINES_TRANSFORMER_CONCEPT_INFO,
                                                                         parse_lines_transformer.GRAMMAR)

FILE_SELECTOR_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(type_system.FILE_SELECTOR_TYPE,
                                                                     types.FILE_SELECTOR_CONCEPT_INFO,
                                                                     parse_file_matcher.GRAMMAR)
