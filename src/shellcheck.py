"""
Main program for shellcheck
"""
import sys

from shellcheck_lib.cli import test_case_parser
from shellcheck_lib.cli import argument_parsing
from shellcheck_lib.cli.argument_parsing import INTERPRETER_FOR_TEST
from shellcheck_lib.execution import full_execution
from shellcheck_lib.script_language.act_script_management import ScriptLanguageSetup
from shellcheck_lib.script_language import python3
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_struct


def main():
    the_cl_arguments = argument_parsing.parse(sys.argv[1:])
    test_case = parse_test_case_source(the_cl_arguments)
    script_language_setup = resolve_script_language(the_cl_arguments)
    full_result = full_execution.execute(script_language_setup,
                                         test_case,
                                         the_cl_arguments.initial_home_dir_path,
                                         the_cl_arguments.execution_directory_root_name_prefix,
                                         the_cl_arguments.is_keep_execution_directory_root)
    print_output_to_stdout(the_cl_arguments,
                           full_result)
    sys.exit(full_result.status.value)


def resolve_script_language(cl_arguments: argument_parsing.Result) -> ScriptLanguageSetup:
    if cl_arguments.interpreter and cl_arguments.interpreter == INTERPRETER_FOR_TEST:
        return python3.new_script_language_setup()
    return python3.new_script_language_setup()


def parse_test_case_source(cl_arguments: argument_parsing.Result) -> test_case_struct.TestCase:
    file_parser = test_case_parser.new_parser()
    source = line_source.new_for_file(cl_arguments.file_path)
    return file_parser.apply(source)


def print_output_to_stdout(cl_arguments: argument_parsing.Result,
                           the_full_result: full_execution.FullResult):
    if cl_arguments.output is argument_parsing.Output.STATUS_CODE:
        print(the_full_result.status.name)
    elif cl_arguments.output is argument_parsing.Output.EXECUTION_DIRECTORY_STRUCTURE_ROOT:
        print(str(the_full_result.execution_directory_structure.root_dir))


main()
