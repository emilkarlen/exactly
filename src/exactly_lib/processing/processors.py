import copy
import os
import pathlib

from exactly_lib import program_info
from exactly_lib.default.program_modes.test_case import test_case_parser
from exactly_lib.execution import full_execution
from exactly_lib.execution.partial_execution import ActPhaseHandling
from exactly_lib.execution.result import FullResult
from exactly_lib.processing import processing_utils
from exactly_lib.processing import test_case_processing as processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.parse.act_phase_source_parser import PlainSourceActPhaseParser
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import ErrorInfo, ProcessError
from exactly_lib.section_document import parse as document_parser
from exactly_lib.section_document.parse import SectionElementParser
from exactly_lib.test_case import error_description
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.instruction_setup import InstructionsSetup
from exactly_lib.util import line_source


class Configuration:
    def __init__(self,
                 split_line_into_name_and_argument_function,
                 instruction_setup: InstructionsSetup,
                 default_handling_setup: TestCaseHandlingSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str = program_info.PROGRAM_NAME + '-'):
        self.default_handling_setup = default_handling_setup
        self.instruction_setup = instruction_setup
        self.split_line_into_name_and_argument_function = split_line_into_name_and_argument_function
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
                                              configuration.default_handling_setup.preprocessor,
                                              _Parser(configuration.split_line_into_name_and_argument_function,
                                                      # configuration.handling_setup.act_phase_setup.parser,
                                                      PlainSourceActPhaseParser(),
                                                      configuration.instruction_setup))


def new_executor_that_should_not_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    return _ExecutorThatSavesAndRestoresEnvironmentVariables(configuration.default_handling_setup.act_phase_setup,
                                                             configuration.is_keep_execution_directory_root,
                                                             configuration.execution_directory_root_name_prefix)


def new_executor_that_may_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    return _Executor(configuration.default_handling_setup.act_phase_setup,
                     configuration.is_keep_execution_directory_root,
                     configuration.execution_directory_root_name_prefix)


class _SourceReader(processing_utils.SourceReader):
    def apply(self,
              test_case_file_path: pathlib.Path) -> str:
        try:
            with test_case_file_path.open() as f:
                return f.read()
        except IOError as ex:
            error_info = processing.ErrorInfo(error_description.of_exception(ex))
            raise ProcessError(error_info)


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
        except document_parser.FileSourceError as ex:
            error_info = ErrorInfo(error_description.of_message('Parse error: ' + ex.source_error.message),
                                   file_path=test_case_file_path,
                                   line=ex.source_error.line,
                                   section_name=ex.maybe_section_name)
            raise ProcessError(error_info)


def act_phase_handling_for_setup(setup: ActPhaseSetup) -> ActPhaseHandling:
    return ActPhaseHandling(setup.source_and_executor_constructor)


class _Executor(processing_utils.Executor):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str = program_info.PROGRAM_NAME + '-'):
        self._act_phase_setup = act_phase_setup
        self._is_keep_execution_directory_root = is_keep_execution_directory_root
        self._execution_directory_root_name_prefix = execution_directory_root_name_prefix

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullResult:
        return full_execution.execute(act_phase_handling_for_setup(self._act_phase_setup),
                                      test_case,
                                      test_case_file_path.parent,
                                      self._execution_directory_root_name_prefix,
                                      self._is_keep_execution_directory_root)


class _ExecutorThatSavesAndRestoresEnvironmentVariables(processing_utils.Executor):
    def __init__(self,
                 act_phase_setup: ActPhaseSetup,
                 is_keep_execution_directory_root: bool,
                 execution_directory_root_name_prefix: str = program_info.PROGRAM_NAME + '-'):
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
