import sys

from shelltest.cli import test_case_parser
from shelltest.cli import argument_parsing
from shelltest.execution import full_execution
from shelltest.script_language.python3 import new_script_language_setup
from shelltest.document import line_source


def main():
    parse_result = argument_parsing.parse(sys.argv)
    file_parser = test_case_parser.new_parser()
    source = line_source.new_for_file(str(parse_result.file_path))

    test_case = file_parser.apply(source)
    script_language_setup = new_script_language_setup()
    full_result = full_execution.execute(script_language_setup,
                                         test_case,
                                         parse_result.initial_home_dir_path,
                                         parse_result.execution_directory_root_name_prefix,
                                         parse_result.is_keep_execution_directory_root)
    print(full_result.status.name)
    sys.exit(full_result.status.value)
