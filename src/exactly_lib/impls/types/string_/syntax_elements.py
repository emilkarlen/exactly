from exactly_lib.util.parse import token_matchers

TEXT_UNTIL_EOL_MARKER = ':>'
TEXT_UNTIL_EOL_TOKEN_MATCHER = token_matchers.is_unquoted_and_equals(TEXT_UNTIL_EOL_MARKER)

HERE_DOCUMENT_SYNTAX_ELEMENT_NAME = 'HERE-DOCUMENT'
