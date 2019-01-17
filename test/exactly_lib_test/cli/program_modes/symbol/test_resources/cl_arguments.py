from typing import List

from exactly_lib.cli.definitions.common_cli_options import SYMBOL_COMMAND
from exactly_lib.cli.definitions.program_modes.test_case import command_line_options
from exactly_lib_test.cli.test_resources import cli_arguments
from exactly_lib_test.processing.test_resources import preprocessor_utils


def arguments(symbol_arguments: List[str]) -> List[str]:
    return [SYMBOL_COMMAND] + symbol_arguments


def explicit_suite__part(suite_file_name: str) -> List[str]:
    return [
        command_line_options.OPTION_FOR_SUITE,
        suite_file_name,
    ]


def explicit_suite_and_case(suite_file_name: str,
                            case_file_name: str) -> List[str]:
    return arguments(
        explicit_suite__part(suite_file_name) + [
            case_file_name,
        ]
    )


def py_preprocessing_and_case(py_preprocessor_source_file_name: str,
                              case_file_name: str) -> List[str]:
    return arguments(
        cli_arguments.py_preprocessing_and_case(py_preprocessor_source_file_name,
                                                case_file_name)
    )


def py_search_replace_preprocessing_and_case(py_preprocessor_source_file_name: str,
                                             to_replace: str,
                                             replacement: str,
                                             case_file_name: str) -> List[str]:
    return arguments(
        preprocessor_utils.cli_args_for_executing_py_file(py_preprocessor_source_file_name,
                                                          [to_replace, replacement])
        +
        [case_file_name]
    )


def individual__definition(case_file: str,
                           symbol_name: str
                           ) -> List[str]:
    return arguments([
        case_file,
        symbol_name
    ])


def individual__references(case_file: str,
                           symbol_name: str
                           ) -> List[str]:
    return arguments([
        case_file,
        symbol_name,
        command_line_options.OPTION_FOR_OPTION_FOR_SYMBOL_REFERENCES,
    ])
