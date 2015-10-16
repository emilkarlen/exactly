import copy
import os
import pathlib

from shellcheck_lib.document import parse as document_parser
from shellcheck_lib.document.parse import SectionElementParser
from shellcheck_lib.execution import full_execution
from shellcheck_lib.execution.partial_execution import ScriptHandling
from shellcheck_lib.execution.result import FullResult
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import processing_utils
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case import test_case_processing as processing
from shellcheck_lib.default.execution_mode.test_case import test_case_parser
from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup
from shellcheck_lib.test_case.test_case_processing import ErrorInfo, ProcessError, Preprocessor
import shellcheck_lib.test_case.test_case_processing


class Configuration:
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 act_phase_setup: ActPhaseSetup,
                 preprocessor: Preprocessor,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self.act_phase_setup = act_phase_setup
        self.instruction_setup = instruction_setup
        self.split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self.preprocessor = preprocessor
        self.is_keep_execution_directory_root = is_keep_execution_directory_root
        self.execution_directory_root_name_prefix = execution_directory_root_name_prefix


def new_processor_that_should_not_pollute_current_process(configuration: Configuration) -> processing.Processor:
    return processing_utils.ProcessorFromAccessorAndExecutor(
        new_accessor(configuration),
        new_executor_that_should_not_pollute_current_processes(configuration))


def new_processor_that_is_allowed_to_pollute_current_process(configuration: Configuration) -> processing.Processor:
    return processing_utils.ProcessorFromAccessorAndExecutor(
        new_accessor(configuration),
        new_executor_that_may_pollute_current_processes(configuration))


def new_accessor(configuration: Configuration) -> processing.Accessor:
    return processing_utils.AccessorFromParts(_SourceReader(),
                                              configuration.preprocessor,
                                              _Parser(configuration.split_line_into_name_and_argument_function,
                                                      configuration.act_phase_setup.parser,
                                                      configuration.instruction_setup))


def new_executor_that_should_not_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    return _ExecutorThatSavesAndRestoresEnvironmentVariables(configuration.act_phase_setup,
                                                             configuration.is_keep_execution_directory_root,
                                                             configuration.execution_directory_root_name_prefix)


def new_executor_that_may_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    return _Executor(configuration.act_phase_setup,
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
                 act_phase_parser: SectionElementParser,
                 instruction_setup: InstructionsSetup):
        self._split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
        self._act_phase_parser = act_phase_parser
        self._instruction_setup = instruction_setup

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        file_parser = test_case_parser.new_parser(self._split_line_into_name_and_argument_function,
                                                  self._act_phase_parser,
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


def script_handling_for_setup(setup: ActPhaseSetup) -> ScriptHandling:
    return ScriptHandling(setup.script_builder_constructor(),
                          setup.executor)


class _Executor(processing_utils.Executor):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self._act_phase_setup = act_phase_setup
        self._is_keep_execution_directory_root = is_keep_execution_directory_root
        self._execution_directory_root_name_prefix = execution_directory_root_name_prefix

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        return full_execution.execute(script_handling_for_setup(self._act_phase_setup),
                                      test_case,
                                      test_case_file_path.parent,
                                      self._execution_directory_root_name_prefix,
                                      self._is_keep_execution_directory_root)


class _ExecutorThatSavesAndRestoresEnvironmentVariables(processing_utils.Executor):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str='shellcheck-'):
        self._polluting_executor = _Executor(act_phase_setup,
                                             is_keep_execution_directory_root,
                                             execution_directory_root_name_prefix)

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        variables_before = copy.deepcopy(os.environ)
        ret_val = self._polluting_executor.apply(test_case_file_path,
                                                 test_case)
        os.environ = variables_before
        return ret_val
