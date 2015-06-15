import pathlib
import argparse

from shellcheck_lib.cli import argument_parsing_utils

from .settings import Output, TestCaseExecutionSettings


INTERPRETER_FOR_TEST = 'test-language'


def parse(argv: list) -> TestCaseExecutionSettings:
    """
    :raises ArgumentParsingError Invalid usage
    :param argv:
    :return:
    """
    output = Output.STATUS_CODE
    is_keep_execution_directory_root = False
    argument_parser = _new_argument_parser()
    namespace = argument_parsing_utils.raise_exception_instead_of_exiting_on_error(argument_parser,
                                                                                   argv)
    if namespace.act:
        output = Output.ACT_PHASE_OUTPUT
    elif namespace.keep:
        output = Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT
        is_keep_execution_directory_root = True
    return TestCaseExecutionSettings(pathlib.Path(namespace.file),
                                     pathlib.Path(namespace.file).parent.resolve(),
                                     output=output,
                                     is_keep_execution_directory_root=is_keep_execution_directory_root)


def _new_argument_parser() -> argparse.ArgumentParser:
    ret_val = argparse.ArgumentParser(description='Execute Shellcheck test case')
    ret_val.add_argument('file',
                         type=str,
                         help='The file containing the test case')
    ret_val.add_argument('-k', '--keep',
                         default=False,
                         action="store_true",
                         help="""\
                        Execution Directory Structure is preserved,
                        and it's root directory is the only output on stdout.""")
    ret_val.add_argument('--act',
                         default=False,
                         action="store_true",
                         help="""\
                        Executes the full test case, but instead of "reporting" the result,
                        the output from the act phase script is emitted:
                        Output on stdout/stderr from the script is printed to stdout/stderr.
                        The exit code from the act script becomes the exit code from the program.""")
    ret_val.add_argument('--interpreter',
                         metavar="INTERPRETER",
                         nargs=1,
                         help="""\
                        Executable that executes the script of the act phase.""")
    return ret_val
