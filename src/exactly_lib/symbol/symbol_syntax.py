from itertools import takewhile
from typing import Tuple, List, Optional

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.util.parse.token import Token

SYMBOL_REFERENCE_BEGIN = '@['
SYMBOL_REFERENCE_END = ']@'


def symbol_reference_syntax_for_name(name: str) -> str:
    return SYMBOL_REFERENCE_BEGIN + name + SYMBOL_REFERENCE_END


class SymbolWithReferenceSyntax:
    """
    Formats a symbol name as a symbol reference, if used as value in str.format()
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self, *args, **kwargs):
        return symbol_reference_syntax_for_name(self.name)


def parse_symbol_reference(token: Token) -> Optional[str]:
    """
    Gives the name of the referenced symbol,
    if the token has the syntax of a symbol reference.
    :returns: None if the token (as a whole) is not a symbol reference,
    otherwise the name of the referenced symbol.
    
    :raise SingleInstructionInvalidArgumentException The token is a symbol reference, but the
    symbol name has invalid syntax.
    """
    return (
        None
        if token.is_quoted
        else
        parse_symbol_reference__from_str(token.string)
    )


def parse_symbol_reference__from_str(token: str) -> Optional[str]:
    """
    Gives the name of the referenced symbol,
    if the token has the syntax of a symbol reference.
    :returns: None if the token (as a whole) is not a symbol reference,
    otherwise the name of the referenced symbol.

    :raise SingleInstructionInvalidArgumentException The token is a symbol reference, but the
    symbol name has invalid syntax.
    """
    if token[:len(SYMBOL_REFERENCE_BEGIN)] == SYMBOL_REFERENCE_BEGIN:
        token = token[len(SYMBOL_REFERENCE_BEGIN):]
        if token[-len(SYMBOL_REFERENCE_END):] == SYMBOL_REFERENCE_END:
            token = token[:-len(SYMBOL_REFERENCE_END)]
            if is_symbol_name(token):
                return token
            else:
                raise SingleInstructionInvalidArgumentException(
                    'Illegal symbol name: `{}\''.format(token))
    return None


class Fragment:
    def __init__(self,
                 value: str,
                 is_symbol: bool):
        self.value = value
        self.is_symbol = is_symbol

    @property
    def is_constant(self) -> bool:
        return not self.is_symbol

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Fragment):
            return self.value == o.value and self.is_symbol == o.is_symbol
        else:
            return False

    def __str__(self):
        fragment_type = 'constant' if self.is_constant else 'symbol'
        return 'Fragment\{{type}, value={value}\}'.format(type=fragment_type,
                                                          value=repr(self.value))


def constant(s: str) -> Fragment:
    return Fragment(s, False)


def symbol(s: str) -> Fragment:
    return Fragment(s, True)


def split(s: str) -> List[Fragment]:
    """
    Splits a string into fragments, according to the syntax of symbol references.

    Each returned fragment is either a string constant or a symbol name.
    :param s:
    :return: [`Fragment`]
    """
    ret_val = []
    while s:
        s, fragments = _extract_fragment(s)
        ret_val.extend(fragments)
    return ret_val


def _extract_fragment(s: str) -> Tuple[str, List[Fragment]]:
    pos, name, rest = _find_symbol_reference(s)
    if pos == -1:
        return '', [Fragment(s, False)]
    if pos == 0:
        return rest, [Fragment(name, True)]
    return rest, [Fragment(s[:pos], False), Fragment(name, True)]


def _find_symbol_reference(s):
    # The constants 2 are the length of SYMBOL_REFERENCE_END/SYMBOL_REFERENCE_END
    sym_ref_pos = s.find(SYMBOL_REFERENCE_BEGIN)
    while sym_ref_pos != -1:
        symbol_name = _extract_symbol_name(s, sym_ref_pos + 2)
        pos_after_symbol_name = sym_ref_pos + 2 + len(symbol_name)
        if symbol_name and s.startswith(SYMBOL_REFERENCE_END, pos_after_symbol_name):
            rest = s[pos_after_symbol_name + 2:]
            return sym_ref_pos, symbol_name, rest
        else:
            sym_ref_pos = s.find(SYMBOL_REFERENCE_BEGIN, pos_after_symbol_name)

    return -1, '', ''


def _extract_symbol_name(s: str, start_idx: int):
    return ''.join(takewhile(_is_identifier, s[start_idx:]))


def _is_identifier(s: str) -> bool:
    return s.isalnum() or s == '_'


def is_symbol_name(s: str) -> bool:
    if not s:
        return False
    for i in range(len(s)):
        ch = s[i:i + 1]
        if ch.isalnum():
            continue
        if ch == '_':
            continue
        return False
    return True


def invalid_symbol_name_error(invalid_name: str) -> str:
    return 'Invalid symbol name: {}.\n{}'.format(invalid_name, SYMBOL_SYNTAX_DESCRIPTION_LINE)


SYMBOL_SYNTAX_DESCRIPTION_LINE = 'A symbol name must only contain alphanum and _'
