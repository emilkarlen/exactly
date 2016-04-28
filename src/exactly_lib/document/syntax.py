import re


class GeneralError(Exception):
    """
    An error that is not an implementation error.
    """
    pass


PHASE_SYNTAX = '[PHASE-NAME]'

TYPE_EMPTY = 0
TYPE_COMMENT = 1
TYPE_PHASE = 2
TYPE_INSTRUCTION = 3

_OPTIONAL_SPACE = '[ \t]*'

EMPTY_LINE_RE = re.compile(_OPTIONAL_SPACE + '$')
COMMENT_LINE_RE = re.compile(_OPTIONAL_SPACE + '#')
PHASE_LINE_RE = re.compile(_OPTIONAL_SPACE + '\[')

_PHASE_NAME_RE = re.compile('\w[\w -.]*\w|\w')
_PHASE_NAME_AFTER_RE = re.compile(']' + _OPTIONAL_SPACE + '$')

_DETECTABLE = (
    (TYPE_EMPTY, EMPTY_LINE_RE),
    (TYPE_COMMENT, COMMENT_LINE_RE),
    (TYPE_PHASE, PHASE_LINE_RE),
)


def is_empty_line(line: str) -> bool:
    return EMPTY_LINE_RE.match(line)


def is_comment_line(line: str) -> bool:
    return COMMENT_LINE_RE.match(line)


def classify_line(line: str) -> int:
    """
    Classifies a line according to the TYPE_ constants.

    :return: One of the TYPE_ constants.
    """
    for type_const, regex in _DETECTABLE:
        if regex.match(line):
            return type_const
    return TYPE_INSTRUCTION


def section_header(section_name: str) -> str:
    """
    Constructs a Phase Header given a Phase Name
    :param section_name:
    """
    return '[' + section_name + ']'


def extract_phase_name_from_phase_line(line: str) -> str:
    """
    :param line: A line that matches _PHASE_LINE_RE
    :raise NonImplementationError: line is not a valid Phase Header
    :return:
    """
    m = PHASE_LINE_RE.match(line)
    after_phase_marker = line[m.end():]
    m = _PHASE_NAME_RE.match(after_phase_marker)
    if not m:
        raise GeneralError()
    ret_val = after_phase_marker[:m.end()]
    after_name = after_phase_marker[m.end():]
    if not _PHASE_NAME_AFTER_RE.match(after_name):
        raise GeneralError()
    return ret_val
