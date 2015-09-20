import pathlib

from shellcheck_lib.document import parse as document_parser
from shellcheck_lib.execution import full_execution
from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general import line_source
from shellcheck_lib.script_language.act_script_management import ScriptLanguageSetup
from shellcheck_lib.test_case import processing_utils
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case import test_case_processing as processing
from shellcheck_lib.default.execution_mode.test_case import test_case_parser
from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_case.test_case_processing import ErrorInfo, ProcessError, Preprocessor
import shellcheck_lib.test_case.test_case_processing


class Configuration:
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 script_language_setup: ScriptLanguageSetup,
                 preprocessor: Preprocessor,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self.script_language_setup = script_language_setup
        self.instruction_setup = instruction_setup
        self.split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self.preprocessor = preprocessor
        self.is_keep_execution_directory_root = is_keep_execution_directory_root
        self.execution_directory_root_name_prefix = execution_directory_root_name_prefix


def new_processor(configuration: Configuration) -> processing.Processor:
    return processing_utils.ProcessorFromAccessorAndExecutor(new_accessor(configuration),
                                                             new_executor(configuration))


def new_accessor(configuration: Configuration) -> processing.Accessor:
    return processing_utils.AccessorFromParts(_SourceReader(),
                                              configuration.preprocessor,
                                              _Parser(configuration.split_line_into_name_and_argument_function,
                                                      configuration.instruction_setup))


def new_executor(configuration: Configuration) -> processing_utils.Executor:
    return _Executor(configuration.script_language_setup,
                     configuration.is_keep_execution_directory_root,
                     configuration.execution_directory_root_name_prefix)


class _SourceReader(processing_utils.SourceReader):
    def apply(self,
              test_case_file_path: pathlib.Path) -> str:
        try:
            with test_case_file_path.open() as f:
                return f.read()
        except IOError as ex:
            error_info = processing.ErrorInfo(exception=ex)
            raise shellcheck_lib.test_case.test_case_processing.ProcessError(error_info)


class _Parser(processing_utils.Parser):
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup):
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self._instruction_setup = instruction_setup

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        file_parser = test_case_parser.new_parser(self._split_line_into_name_and_argument_function,
                                                  self._instruction_setup)
        source = line_source.new_for_string(test_case_plain_source)
        try:
            return file_parser.apply(source)
        except document_parser.SourceError as ex:
            error_info = ErrorInfo(message='Parsing error: ' + ex.message,
                                   file_path=test_case_file_path,
                                   line=ex.line,
                                   exception=ex)
            raise ProcessError(error_info)


class _Executor(processing_utils.Executor):
    def __init__(self,
                 script_language_setup: ScriptLanguageSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self._script_language_setup = script_language_setup
        self._is_keep_execution_directory_root = is_keep_execution_directory_root
        self._execution_directory_root_name_prefix = execution_directory_root_name_prefix

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: processing.TestCase) -> FullResult:
        return full_execution.execute(self._script_language_setup,
                                      test_case,
                                      test_case_file_path.parent,
                                      self._execution_directory_root_name_prefix,
                                      self._is_keep_execution_directory_root)
