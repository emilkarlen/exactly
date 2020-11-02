import itertools

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse import token

TOKENS_WITH_INVALID_SYNTAX = list(itertools.chain.from_iterable(
    [
        [
            NameAndValue('unmatched {} at start of string'.format(token.QUOTE_NAME_FOR_TYPE[quote_type].singular),
                         token.QUOTE_CHAR_FOR_TYPE[quote_type] + 'plain'
                         ),
            NameAndValue('unmatched {} at end of string'.format(token.QUOTE_NAME_FOR_TYPE[quote_type].singular),
                         'plain' + token.QUOTE_CHAR_FOR_TYPE[quote_type]
                         ),
            NameAndValue('only {} char'.format(token.QUOTE_NAME_FOR_TYPE[quote_type].singular),
                         token.QUOTE_CHAR_FOR_TYPE[quote_type]
                         ),
        ]
        for quote_type in token.QuoteType
    ]
))
