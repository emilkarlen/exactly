import sys


def which_python() -> str:
    if sys.platform == 'win23':
        return sys.executable
    else:
        return '$(which python)'


def command_that_copes_stdin_to_stdout() -> str:
    if sys.platform == 'win32':
        return 'echo'
    else:
        return 'cat'


def command_that_prints_to_stderr(string_to_print: str) -> str:
    if sys.platform == 'win32':
        return 'Write-Error "{}"'.format(string_to_print)  # do not know how to suppress new-line
    else:
        return "echo '{}' >&2".format(string_to_print)


def command_that_prints_to_stdout(string_to_print: str) -> str:
    if sys.platform == 'win32':
        return 'Write-Output "{}"'.format(string_to_print)  # do not know how to suppress new-line
    else:
        return "echo '{}'".format(string_to_print)


def command_that_prints_line_to_stdout(line_contents: str) -> str:
    if sys.platform == 'win32':
        return 'Write-Output "{}"'.format(line_contents)
    else:
        return "echo '{}'".format(line_contents)


def command_that_exits_with_code(exit_code: int) -> str:
    return 'exit {}'.format(exit_code)


def command_that_prints_cwd_line_to_stdout() -> str:
    if sys.platform == 'win32':
        return 'Write-Output %cd%'
    else:
        return 'echo $PWD'


def command_that_prints_value_of_environment_variable_to_stdout(var_name: str) -> str:
    if sys.platform == 'win32':
        return 'echo %{}%'.format(var_name)
    else:
        return 'echo ${}'.format(var_name)


def program_that_sleeps_at_least(number_of_seconds: int) -> str:
    if sys.platform == 'win32':
        return 'timeout {}'.format(number_of_seconds)
    else:
        return 'sleep {}'.format(number_of_seconds)
