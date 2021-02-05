import re

TYPE_EMPTY = 0
TYPE_COMMENT = 1
TYPE_SECTION = 2
TYPE_INSTRUCTION = 3

_OPTIONAL_SPACE = '[ \t]*'

LINE_COMMENT_MARKER = '#'

EMPTY_LINE_RE = re.compile(_OPTIONAL_SPACE + '$')
COMMENT_LINE_RE = re.compile(_OPTIONAL_SPACE + '#')
SECTION_LINE_RE = re.compile(_OPTIONAL_SPACE + '\[')

_SECTION_NAME_RE = re.compile('\w[\w -.]*\w|\w')
_SECTION_NAME_AFTER_RE = re.compile(']' + _OPTIONAL_SPACE + '$')

_DETECTABLE = (
    (TYPE_EMPTY, EMPTY_LINE_RE),
    (TYPE_COMMENT, COMMENT_LINE_RE),
    (TYPE_SECTION, SECTION_LINE_RE),
)


def is_empty_line(line: str) -> bool:
    return bool(EMPTY_LINE_RE.match(line))


def is_comment_line(line: str) -> bool:
    return bool(COMMENT_LINE_RE.match(line))


def is_empty_or_comment_line(line: str) -> bool:
    return is_empty_line(line) or is_comment_line(line)


def is_section_header_line(line: str) -> bool:
    return bool(SECTION_LINE_RE.match(line))


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


def extract_section_name_from_section_line(line: str) -> str:
    """
    :param line: A line that matches SECTION_LINE_RE
    :raise ValueError: line is not a valid Phase Header
    :return:
    """
    m = SECTION_LINE_RE.match(line)
    after_phase_marker = line[m.end():]
    m = _SECTION_NAME_RE.match(after_phase_marker)
    if not m:
        raise ValueError('Cannot parse section name from: "%s"' % after_phase_marker)
    ret_val = after_phase_marker[:m.end()]
    after_name = after_phase_marker[m.end():]
    if not _SECTION_NAME_AFTER_RE.match(after_name):
        raise ValueError('Invalid text after section name: "%s"' % after_name)
    return ret_val
