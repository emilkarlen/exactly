import pathlib
import subprocess
import tempfile
from typing import List

from exactly_lib import program_info
from exactly_lib.common.report_rendering.text_doc import MinorTextRenderer
from exactly_lib.processing.test_case_processing import Preprocessor, ProcessError, ErrorInfo
from exactly_lib.section_document.source_location import source_location_path_of
from exactly_lib.test_case import error_description
from exactly_lib.util.render import combinators as comb
from exactly_lib.util.simple_textstruct import structure
from exactly_lib.util.simple_textstruct.rendering import blocks


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
                 external_program: List[str]):
        self.external_program = external_program

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_source: str) -> str:
        command_line = self.external_program + [str(test_case_file_path.name)]
        try:
            with tempfile.TemporaryFile(prefix=program_info.PROGRAM_NAME + '-stdout-',
                                        mode='w+') as stdout_file:
                with tempfile.TemporaryFile(prefix=program_info.PROGRAM_NAME + '-stderr-',
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
                        raise ProcessError(self.__error_info(
                            error_description.of_external_process_error(exitcode,
                                                                        stderr_contents,
                                                                        self.__error_message()),
                            test_case_file_path))
        except ProcessError as ex:
            raise ex
        except Exception as ex:
            raise ProcessError(self.__error_info(
                error_description.of_exception(ex,
                                               self.__error_message()),
                test_case_file_path))

    @staticmethod
    def __error_info(ed: error_description.ErrorDescription,
                     test_case_file_path: pathlib.Path) -> ErrorInfo:
        return ErrorInfo(ed,
                         source_location_path_of(test_case_file_path,
                                                 None))

    def __error_message(self) -> MinorTextRenderer:
        return blocks.MinorBlocksOfSingleLineObject(
            comb.ConstantR(structure.StringLineObject(
                'Error from preprocessing by: ' + str(self.external_program))
            )
        )
