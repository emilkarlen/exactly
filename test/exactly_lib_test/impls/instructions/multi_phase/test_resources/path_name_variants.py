from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes

SINGLE_TOKEN_NAME = 'single_token_dir_name'
MULTI_LINE_NAME = 'a\nname\nthat\nspans\nmultiple\nlines\n'
SF = StringFormatter({
    'single_token_name': SINGLE_TOKEN_NAME,
    'quoted_multi_line_name': surrounded_by_hard_quotes(MULTI_LINE_NAME),
})

SOURCE_LAYOUT_CASES = [
    NIE(
        'all arguments on first line',
        input_value=SF.format('{single_token_name}'),
        expected_value=SINGLE_TOKEN_NAME,
    ),
    NIE(
        'path argument on following line',
        input_value=SF.format('\n {single_token_name}'),
        expected_value=SINGLE_TOKEN_NAME,
    ),
    NIE(
        'multi line path argument on following line',
        input_value=SF.format('\n {quoted_multi_line_name}'),
        expected_value=MULTI_LINE_NAME,
    ),
]
