from exactly_lib.util.parse import token_matchers
from . import reserved_words

IS_RESERVED_WORD = token_matchers.is_unquoted_and_equals_any(reserved_words.RESERVED_TOKENS)

IS_PAREN__BEGIN = token_matchers.is_unquoted_and_equals(reserved_words.PAREN_BEGIN)
IS_PAREN__END = token_matchers.is_unquoted_and_equals(reserved_words.PAREN_END)

IS_BRACKET__BEGIN = token_matchers.is_unquoted_and_equals(reserved_words.BRACKET_BEGIN)
IS_BRACKET__END = token_matchers.is_unquoted_and_equals(reserved_words.BRACKET_END)
