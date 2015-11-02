import pathlib
import subprocess
import tempfile

from shellcheck_lib.test_case import error_description
from shellcheck_lib.test_case.test_case_processing import Preprocessor, ProcessError, ErrorInfo


class IdentityPreprocessor(Preprocessor):
    """
    A pre-processor that does nothing.
    """

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        return test_case_source


IDENTITY_PREPROCESSOR = IdentityPreprocessor()


class PreprocessorViaExternalProgram(Preprocessor):
    """
    A pre-processor that transforms the contents of a test case file
    by executing an external program, with the test case file as
    argument.
    """

    def __init__(self,
                 external_program: list):
        self.external_program = external_program

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        command_line = self.external_program + [str(test_case_file_path)]
        try:
            with tempfile.TemporaryFile(prefix='shellcheck-stdout-',
                                        mode='w+') as stdout_file:
                with tempfile.TemporaryFile(prefix='shellcheck-stderr-',
                                            mode='w+') as stderr_file:
                    exitcode = subprocess.call(command_line,
                                               cwd=str(test_case_file_path.parent),
                                               stdout=stdout_file,
                                               stderr=stderr_file)
                    if exitcode == 0:
                        stdout_file.seek(0)
                        stdout_contents = stdout_file.read()
                        return str(stdout_contents)
                    else:
                        stderr_file.seek(0)
                        stderr_contents = stderr_file.read()
                        raise self.__new_process_error(
                            error_description.of_external_process_error(exitcode,
                                                                        stderr_contents,
                                                                        self.__error_message()),
                            test_case_file_path)
        except Exception as ex:
            raise self.__new_process_error(
                error_description.of_exception(ex,
                                               self.__error_message()),
                test_case_file_path)

    @staticmethod
    def __new_process_error(ed: error_description.ErrorDescription,
                            test_case_file_path: pathlib.Path) -> ProcessError:
        return ProcessError(ErrorInfo(ed,
                                      test_case_file_path))

    def __error_message(self) -> str:
        return 'Error from preprocessing by: ' + str(self.external_program)
