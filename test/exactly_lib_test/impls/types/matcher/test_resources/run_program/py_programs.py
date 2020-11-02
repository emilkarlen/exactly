from typing import List

EXIT_CODE_FOR_SUCCESS = 0


def pgm_that_exists_with_zero_exit_code_iff_arguments_are_expected(expected: List[str]) -> str:
    return _PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ARGUMENTS_ARE_EXPECTED.format(
        expected_arg_list=repr(expected)
    )


def pgm_that_exists_with_zero_exit_code_iff_stdin_is_not_expected(expected: str) -> str:
    return _PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_STDIN_IS_EXPECTED.format(
        expected=repr(expected)
    )


# NOTE: Some env vars (probably for executing python), are included automatically.
# Because of this, we cannot check for equality, but must instead check that
# all given env vars are included in the actual env.

_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_STDIN_IS_EXPECTED = """\
import sys;

expected_stdin = {expected}

actual_stdin = sys.stdin.read()

sys.exit(int(actual_stdin != expected_stdin))
"""

_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ARGUMENTS_ARE_EXPECTED = """\
import sys;

expected = {expected_arg_list}

sys.exit(int(expected != sys.argv[1:]))
"""
