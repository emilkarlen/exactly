from typing import List

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NIE


def no_leading_or_trailing_space_cases() -> List[NameAndValue[List[str]]]:
    return [
        NameAndValue(
            'no lines',
            [],
        ),
        NameAndValue(
            'single line not ended by new-line',
            ['not new-line'],
        ),
        NameAndValue(
            'multiple lines, last not ended by new-line',
            ['first\n', 'last'],
        ),
        NameAndValue(
            'multiple lines - empty sequence before non-empty contents (preceded by non-empty lines)'
            ' - not ended by new-line',
            ['first non-empty\n', '\n', ' \n', 'last non-empty'],
        ),
    ]


def only_leading_space_cases() -> List[NameAndValue[List[str]]]:
    return [
        NameAndValue(
            'single empty line',
            ['\n', 'end'],
        ),
        NameAndValue(
            'single line with space',
            ['  \n', 'end'],
        ),
        NameAndValue(
            'single line with space (tab)',
            ['\t\n', 'end'],
        ),
        NameAndValue(
            'multiple empty lines',
            ['\n', '\n', '\n', 'end'],
        ),
        NameAndValue(
            'leading just-space lines and just-space lines in the middle',
            ['\n', '  \n', 'middle\n', '\n', ' \n', 'end'],
        ),
    ]


def trailing_new_lines_cases_w_leading_space() -> List[NIE[List[str], List[str]]]:
    return [
        NIE('single line (non-empty) ended by new-line',
            input_value=['last\n'],
            expected_value=['last'],
            ),
        NIE('single line (empty) ended by new-line',
            input_value=['\n'],
            expected_value=[],
            ),
        NIE('non-empty and empty line',
            input_value=['1\n', '\n'],
            expected_value=['1'],
            ),
        NIE('multiple lines - first non-empty',
            input_value=['1\n', '\n', '\n'],
            expected_value=['1'],
            ),
        NIE('multiple lines - every line empty',
            input_value=['\n', '\n', '\n'],
            expected_value=[],
            ),
        NIE('multiple lines - empty sequence before non-empty contents - ended by new-line',
            input_value=['\n', '\n', 'non-empty\n'],
            expected_value=['\n', '\n', 'non-empty'],
            ),
        NIE('multiple lines - empty sequence before non-empty contents - ended sequence of empty lines',
            input_value=['\n', '\n', 'non-empty\n', '\n', '\n'],
            expected_value=['\n', '\n', 'non-empty'],
            ),
    ]


def just_space_cases() -> List[NameAndValue[List[str]]]:
    return [
        NameAndValue(
            'single empty line',
            ['\n'],
        ),
        NameAndValue(
            'single line with just space, wo new-line',
            ['   \t'],
        ),
        NameAndValue(
            'single line with just space, w new-line',
            ['   \t\n'],
        ),
        NameAndValue(
            'multiple lines, wo ending new-line',
            ['   \t\n', '\n', '  \n', '\t\n', '    '],
        ),
        NameAndValue(
            'multiple lines, w ending new-line',
            ['   \t\n', '\n', '  \n', '\t\n', '    \n'],
        ),
    ]
