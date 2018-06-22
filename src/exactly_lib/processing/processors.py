import os
import pathlib
from typing import Optional

from exactly_lib import program_info
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.configuration import PredefinedProperties, ExecutionConfiguration
from exactly_lib.execution.full_execution import execution
from exactly_lib.execution.full_execution.result import FullExeResult
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing import processing_utils
from exactly_lib.processing import test_case_processing as processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.parse import test_case_parser
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import ErrorInfo, ProcessError, TestCaseSetup, AccessorError, \
    AccessErrorType
from exactly_lib.section_document import exceptions
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case import error_description
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib.util.line_source import source_location_path_of_non_empty_location_path
from exactly_lib.util.std import StdOutputFiles


class TestCaseDefinition:
    """Test case configuration that is defined in code."""

    def __init__(self,
                 test_case_parsing_setup: TestCaseParsingSetup,
                 predefined_properties: PredefinedProperties):
        self.test_case_parsing_setup = test_case_parsing_setup
        self.predefined_properties = predefined_properties

    @property
    def parsing_setup(self) -> TestCaseParsingSetup:
        return self.test_case_parsing_setup


class Configuration:
    def __init__(self,
                 test_case_definition: TestCaseDefinition,
                 default_handling_setup: TestCaseHandlingSetup,
                 act_phase_os_process_executor: ActPhaseOsProcessExecutor,
                 is_keep_sandbox: bool,
                 sandbox_root_dir_resolver: SandboxRootDirNameResolver =
                 sandbox_dir_resolving.mk_tmp_dir_with_prefix(program_info.PROGRAM_NAME + '-'),
                 exe_atc_and_skip_assertions: Optional[StdOutputFiles] = None):
        self.default_handling_setup = default_handling_setup
        self.act_phase_os_process_executor = act_phase_os_process_executor
        self.test_case_definition = test_case_definition
        self.is_keep_sandbox = is_keep_sandbox
        self.exe_atc_and_skip_assertions = exe_atc_and_skip_assertions
        self.sandbox_root_dir_resolver = sandbox_root_dir_resolver


def new_processor_that_should_not_pollute_current_process(configuration: Configuration) -> processing.Processor:
    return processing_utils.ProcessorFromAccessorAndExecutor(
        new_accessor(configuration),
        new_executor_that_should_not_pollute_current_processes(configuration))


def new_processor_that_is_allowed_to_pollute_current_process(configuration: Configuration) -> processing.Processor:
    return processing_utils.ProcessorFromAccessorAndExecutor(
        new_accessor(configuration),
        new_executor_that_may_pollute_current_processes(configuration))


def new_accessor(configuration: Configuration) -> processing.Accessor:
    return processing_utils.AccessorFromParts(
        _SourceReader(),
        configuration.default_handling_setup.preprocessor,
        _Parser(configuration.test_case_definition.parsing_setup),
        configuration.default_handling_setup.transformer)


def new_executor_that_should_not_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    # Currently, the executor does not pollute the current process
    return new_executor_that_may_pollute_current_processes(configuration)


def new_executor_that_may_pollute_current_processes(configuration: Configuration) -> processing_utils.Executor:
    return _Executor(ExecutionConfiguration(dict(os.environ),
                                            configuration.act_phase_os_process_executor,
                                            configuration.sandbox_root_dir_resolver,
                                            configuration.test_case_definition.predefined_properties.predefined_symbols,
                                            configuration.exe_atc_and_skip_assertions),
                     configuration.default_handling_setup.act_phase_setup,
                     configuration.is_keep_sandbox)


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
    def __init__(self, test_case_parsing_setup: TestCaseParsingSetup):
        self._test_case_parsing_setup = test_case_parsing_setup

    def apply(self,
              test_case: TestCaseSetup,
              test_case_plain_source: str) -> test_case_doc.TestCase:
        file_parser = test_case_parser.new_parser(self._test_case_parsing_setup)
        source = ParseSource(test_case_plain_source)
        try:
            return file_parser.apply(test_case, source)
        except exceptions.FileSourceError as ex:
            error_info = ErrorInfo(error_description.syntax_error_of_message(ex.source_error.message),
                                   source_location_path_of_non_empty_location_path(ex.location_path),
                                   section_name=ex.maybe_section_name)
            raise ProcessError(error_info)

        except exceptions.FileAccessError as ex:
            error_info = ErrorInfo(error_description.syntax_error_of_message(ex.message),
                                   source_location_path_of_non_empty_location_path(ex.location_path))
            raise AccessorError(AccessErrorType.FILE_ACCESS_ERROR,
                                error_info)


def act_phase_handling_for_setup(setup: ActPhaseSetup) -> ActPhaseHandling:
    return ActPhaseHandling(setup.source_and_executor_constructor)


class _Executor(processing_utils.Executor):
    def __init__(self,
                 exe_conf: ExecutionConfiguration,
                 default_act_phase_setup: ActPhaseSetup,
                 is_keep_sandbox: bool):
        self.default_act_phase_setup = default_act_phase_setup
        self._is_keep_sandbox = is_keep_sandbox
        self._exe_conf = exe_conf

    def apply(self,
              test_case_file_path: pathlib.Path,
              test_case: test_case_doc.TestCase) -> FullExeResult:
        dir_containing_test_case_file = test_case_file_path.parent.resolve()
        return execution.execute(self._exe_conf,
                                 ConfigurationBuilder(dir_containing_test_case_file,
                                                      dir_containing_test_case_file,
                                                      act_phase_handling_for_setup(self.default_act_phase_setup)),
                                 self._is_keep_sandbox,
                                 test_case)
