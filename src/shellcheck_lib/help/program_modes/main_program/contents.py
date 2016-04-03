from shellcheck_lib.util.textformat.parse import normalize_and_parse


def test_case_overview_help() -> list:
    return normalize_and_parse(_test_case_overview_help_text)


_test_case_overview_help_text = """\
TODO Runs a program in a temporary directory, and tests the result,
according to specifications in a test-case file.


Or runs a test-suite.


A test case is a sequence of "instructions". Each instruction belongs to the "phase".

The phases are executed in the following order:
"""
