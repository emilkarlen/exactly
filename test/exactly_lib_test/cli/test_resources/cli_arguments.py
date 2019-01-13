from typing import List

from exactly_lib_test.processing.test_resources import preprocessor_utils


def py_preprocessing_and_case(py_preprocessor_source_file_name: str,
                              case_file_name: str) -> List[str]:
    return (preprocessor_utils.cli_args_for_executing_py_file(py_preprocessor_source_file_name)
            +
            [case_file_name])
