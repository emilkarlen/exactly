from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def py_pgm_that_exits_with_value_on_command_line(stderr_output: str) -> str:
    return """\
import sys

sys.stderr.write('{}')
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


def py_pgm_with_stdout_stderr_exit_code(stdout_output: str,
                                        stderr_output: str,
                                        exit_code: int) -> str:
    return """\
import sys

sys.stdout.write('{stdout}')
sys.stderr.write('{stderr}')
sys.exit({exit_code})
""".format(stdout=stdout_output,
           stderr=stderr_output,
           exit_code=exit_code)


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


def single_line_pgm_that_prints_to_stdout(output: str) -> str:
    return single_line_pgm_that_prints_to(ProcOutputFile.STDOUT, output)


def single_line_pgm_that_prints_to_stderr(output: str) -> str:
    return single_line_pgm_that_prints_to(ProcOutputFile.STDERR, output)


def single_line_pgm_that_prints_to(output_channel: ProcOutputFile, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE.format(channel=_CHANNEL_NAMES[output_channel],
                                                                str=output)


_SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE = 'import sys; sys.{channel}.write("""{str}""")'


def single_line_pgm_that_prints_to_stdout_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line(ProcOutputFile.STDOUT, output)


def single_line_pgm_that_prints_to_stderr_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line(ProcOutputFile.STDERR, output)


def single_line_pgm_that_prints_to_with_new_line(output_channel: ProcOutputFile, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE.format(channel=_CHANNEL_NAMES[output_channel],
                                                             str=output)


_SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE = 'import sys; sys.{channel}.write("""{str}\\n""")'

_CHANNEL_NAMES = {
    ProcOutputFile.STDOUT: 'stdout',
    ProcOutputFile.STDERR: 'stderr',
}
