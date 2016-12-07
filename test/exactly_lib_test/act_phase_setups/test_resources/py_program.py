from exactly_lib_test.test_resources.process import SubProcessResult


def write_string_to_stdout(string_to_print) -> list:
    return ['import sys',
            "sys.stdout.write('{}\\n')".format(string_to_print)]


def write_string_to_stderr(string_to_print) -> list:
    return ['import sys',
            "sys.stderr.write('{}\\n')".format(string_to_print)]


def exit_with_code(exit_code: int) -> list:
    return [
        'import sys',
        "sys.exit({})".format(exit_code)
    ]


def copy_stdin_to_stdout() -> list:
    return [
        'import sys',
        "sys.stdout.write(sys.stdin.read())"
    ]


def write_value_of_environment_variable_to_stdout(var_name: str) -> list:
    return [
        'import os',
        "print(os.environ['{}'])".format(var_name),
    ]


def write_cwd_to_stdout() -> list:
    return [
        'import os',
        "print(os.getcwd())"
    ]


def program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds: int) -> list:
    return [
        'import time',
        'time.sleep({})'.format(number_of_seconds),
    ]


def program_that_prints_and_exits_with_exit_code(output: SubProcessResult) -> str:
    return _PY_PGM_THAT_PRINTS_AND_EXITS_WITH_EXIT_CODE.format(exit_code=output.exitcode,
                                                               stdout=output.stdout,
                                                               stderr=output.stderr)


_PY_PGM_THAT_PRINTS_AND_EXITS_WITH_EXIT_CODE = """\
import sys
sys.stdout.write('{stdout}')
sys.stderr.write('{stderr}')
sys.exit({exit_code})
"""
