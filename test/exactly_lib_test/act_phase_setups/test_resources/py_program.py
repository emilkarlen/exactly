def write_string_to_stdout(string_to_print) -> list:
    return ['import sys',
            "sys.stdout.write('{}')".format(string_to_print)]


def write_string_to_stderr(string_to_print) -> list:
    return ['import sys',
            "sys.stderr.write('{}')".format(string_to_print)]


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
        'import sys',
        'import os',
        "sys.stdout.write(os.environ['{}'])".format(var_name)
    ]


def write_cwd_to_stdout() -> list:
    return [
        'import sys',
        'import os',
        "sys.stdout.write(os.getcwd())"
    ]
