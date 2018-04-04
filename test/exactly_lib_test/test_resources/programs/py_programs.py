from exactly_lib.util.process_execution.process_output_files import ProcOutputFile


def py_pgm_that_exits_with_value_on_command_line(stderr_output: str) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


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
