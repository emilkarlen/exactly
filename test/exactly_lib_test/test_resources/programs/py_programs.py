from typing import Dict

from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def py_pgm_that_copies_stdin_to_stdout() -> str:
    return """\
import sys

sys.stdout.writelines(sys.stdin.readlines())
"""


def copy_stdin_to_stderr_and_exit_with(exit_code: int) -> str:
    return """\
import sys
sys.stderr.write(sys.stdin.read())
sys.exit({})
""".format(exit_code)


def py_pgm_that_exits_with_1st_value_on_command_line(stderr_output: str) -> str:
    return """\
import sys

sys.stderr.write('{}')
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


def py_pgm_with_stdout_stderr_exit_code(stdout_output: str = '',
                                        stderr_output: str = '',
                                        exit_code: int = 0) -> str:
    return """\
import sys

sys.stdout.write('{stdout}')
sys.stderr.write('{stderr}')
sys.exit({exit_code})
""".format(stdout=stdout_output,
           stderr=stderr_output,
           exit_code=exit_code)


def exit_with(exit_code: int = 0) -> str:
    return """\
import sys

sys.exit({})
""".format(exit_code)


def exit_with_0() -> str:
    return ''


def py_pgm_that_writes_os_linesep_to_stdout() -> str:
    return """\
import sys
import os

sys.stdout.write(os.linesep)
"""


def py_pgm_that_writes_new_line_to_stdout() -> str:
    return """\
import sys

sys.stdout.write('\\n')
"""


def py_pgm_that_writes_tab_character_to_stdout() -> str:
    return """\
import sys

sys.stdout.write('\\t')
"""


def py_pgm_with_stdout_stderr_and_sleep_in_between(stdout_output_before_sleep: str,
                                                   stderr_output_before_sleep: str,
                                                   stdout_output_after_sleep: str,
                                                   stderr_output_after_sleep: str,
                                                   sleep_seconds: int,
                                                   exit_code: int) -> str:
    return """\
import sys
import time

def write_to(f, s):
  f.write(s)
  f.flush()

write_to(sys.stdout, '{stdout_output_before_sleep}')
write_to(sys.stderr, '{stderr_output_before_sleep}')

time.sleep({sleep_seconds})

write_to(sys.stdout, '{stdout_output_after_sleep}')
write_to(sys.stderr, '{stderr_output_after_sleep}')

sys.exit({exit_code})
""".format(stdout_output_before_sleep=stdout_output_before_sleep,
           stderr_output_before_sleep=stderr_output_before_sleep,
           stdout_output_after_sleep=stdout_output_after_sleep,
           stderr_output_after_sleep=stderr_output_after_sleep,
           sleep_seconds=sleep_seconds,
           exit_code=exit_code)


def single_line_pgm_that_exists_with(exit_code: int) -> str:
    return _SINGLE_LINE_PGM_THAT_EXITS_WITH_CODE.format(exit_code)


def single_line_pgm_that_prints_to_stdout(output: str) -> str:
    return single_line_pgm_that_prints_to(ProcOutputFile.STDOUT, output)


def single_line_pgm_that_prints_to_stderr(output: str) -> str:
    return single_line_pgm_that_prints_to(ProcOutputFile.STDERR, output)


def single_line_pgm_that_prints_to(output_channel: ProcOutputFile, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE.format(channel=_CHANNEL_NAMES[output_channel],
                                                                str=output)


def single_line_pgm_that_prints_to_stdout_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line(ProcOutputFile.STDOUT, output)


def single_line_pgm_that_prints_to_stderr_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line(ProcOutputFile.STDERR, output)


def single_line_pgm_that_prints_to_with_new_line(output_channel: ProcOutputFile, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE.format(channel=_CHANNEL_NAMES[output_channel],
                                                             str=output)


def pgm_that_exists_with_zero_exit_code_iff_environment_vars_not_included(expected: Dict[str, str]) -> str:
    return _PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ENVIRONMENT_VARS_IS_NOT_INCLUDED.format(
        expected_environment=repr(expected)
    )


_SINGLE_LINE_PGM_THAT_EXITS_WITH_CODE = 'import sys; sys.exit({})'

_SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE = 'import sys; sys.{channel}.write("""{str}""")'

_SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE = 'import sys; sys.{channel}.write("""{str}\\n""")'

_CHANNEL_NAMES = {
    ProcOutputFile.STDOUT: 'stdout',
    ProcOutputFile.STDERR: 'stderr',
}

_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ENVIRONMENT_VARS_IS_NOT_INCLUDED = """\
import os;
import sys;

expected_env_vars = {expected_environment}

actual_env_vars = dict(os.environ)

for (key, value) in expected_env_vars.items():

  if not key in actual_env_vars:
     sys.stderr.write('Missing key: ' + key)
     sys.exit(1)

  actual_value = actual_env_vars[key]
  if value != actual_value:
     sys.stderr.write('Different value: %s != %s' % (key, actual_value))
     sys.exit(1)

sys.exit(0)
"""
