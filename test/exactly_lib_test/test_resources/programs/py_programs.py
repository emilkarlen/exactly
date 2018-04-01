def py_pgm_that_exits_with_value_on_command_line(stderr_output: str) -> str:
    return """
import sys

sys.stderr.write('{}');
val = int(sys.argv[1])
sys.exit(val)
""".format(stderr_output)


def single_line_pgm_that_prints_to_stdout_no_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_no_new_line('stdout', output)


def single_line_pgm_that_prints_to_stderr_no_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_no_new_line('stderr', output)


def single_line_pgm_that_prints_to_no_new_line(channel: str, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE.format(channel=channel,
                                                                str=output)


_SINGLE_LINE_PGM_THAT_PRINTS_WITHOUT_NEW_LINE = 'import sys; sys.{channel}.write("""{str}""")'


def single_line_pgm_that_prints_to_stdout_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line('stdout', output)


def single_line_pgm_that_prints_to_stderr_with_new_line(output: str) -> str:
    return single_line_pgm_that_prints_to_with_new_line('stderr', output)


def single_line_pgm_that_prints_to_with_new_line(channel: str, output: str) -> str:
    return _SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE.format(channel=channel,
                                                             str=output)


_SINGLE_LINE_PGM_THAT_PRINTS_WITH_NEW_LINE = 'import sys; sys.{channel}.write("""{str}\\n""")'

if __name__ == '__main__':
    print(single_line_pgm_that_prints_to_with_new_line('stdout', 'hello'))
