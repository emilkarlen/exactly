from shelltest.cli import test_case_parser
from shelltest.cli import argument_parsing
from shelltest.execution import full_execution
from shelltest.execution.result import FullResult
from shelltest.script_language.python3 import new_script_language_setup
from shelltest.general import line_source


class Result(tuple):
    def __new__(cls,
                full_result: FullResult):
        return tuple.__new__(cls, (full_result,))

    @property
    def full_result(self) -> FullResult:
        return self[0]


def execute(argv: list) -> Result:
    parse_result = argument_parsing.parse(argv)
    file_parser = test_case_parser.new_parser()
    source = line_source.new_for_file(parse_result.file_path)

    test_case = file_parser.apply(source)
    script_language_setup = new_script_language_setup()
    full_result = full_execution.execute(script_language_setup,
                                         test_case,
                                         parse_result.initial_home_dir_path,
                                         parse_result.execution_directory_root_name_prefix,
                                         parse_result.is_keep_execution_directory_root)
    return Result(full_result)
