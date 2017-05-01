from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parser_implementations.token import Token

SYMBOL_REFERENCE_BEGIN = '@['
SYMBOL_REFERENCE_END = ']@'


def symbol_reference_syntax_for_name(name: str) -> str:
    return SYMBOL_REFERENCE_BEGIN + name + SYMBOL_REFERENCE_END


def parse_symbol_reference(path_argument: Token) -> str:
    """
    Gives the name of the referenced symbol,
    if the token has the syntax of a symbol reference.
    :returns: None if the token (as a whole) is not a symbol reference,
    otherwise the name of the referenced symbol.
    
    :raise SingleInstructionInvalidArgumentException The token is a symbol reference, but the
    symbol name has invalid syntax.
    """
    if path_argument.is_quoted:
        return None
    s = path_argument.string
    if s[:len(SYMBOL_REFERENCE_BEGIN)] == SYMBOL_REFERENCE_BEGIN:
        s = s[len(SYMBOL_REFERENCE_BEGIN):]
        if s[-len(SYMBOL_REFERENCE_END):] == SYMBOL_REFERENCE_END:
            s = s[:-len(SYMBOL_REFERENCE_END)]
            if is_symbol_name(s):
                return s
            else:
                raise SingleInstructionInvalidArgumentException(
                    'Illegal symbol name: `{}\''.format(s))
    return None


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
