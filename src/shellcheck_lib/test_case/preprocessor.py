import pathlib

from shellcheck_lib.test_case.test_case_processing import Preprocessor


class IdentityPreprocessor(Preprocessor):
    """
    A pre-processor that does nothing.
    """

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return test_case_source


class PreprocessorViaExternalProgram(Preprocessor):
    """
    A pre-processor that transforms the contents of a test case file
    by executing an external program, with the test case file as
    argument.
    """

    def __init__(self,
                 external_program: str):
        self.external_program = external_program

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return test_case_source
