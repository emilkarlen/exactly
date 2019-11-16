import enum
import pathlib
from typing import Optional

from exactly_lib import program_info
from exactly_lib.execution import sandbox_dir_resolving
from exactly_lib.execution.sandbox_dir_resolving import SandboxRootDirNameResolver
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup


class ReportingOption(enum.Enum):
    STATUS_CODE = 1
    SANDBOX_DIRECTORY_STRUCTURE_ROOT = 2
    ACT_PHASE_OUTPUT = 3


class TestCaseExecutionSettings:
    """Settings derived after parsing of command line arguments."""

    def __init__(self,
                 test_case_file_path: pathlib.Path,
                 initial_hds_dir_path: pathlib.Path,
                 output: ReportingOption,
                 handling_setup: TestCaseHandlingSetup,
                 sandbox_root_dir_resolver: SandboxRootDirNameResolver =
                 sandbox_dir_resolving.mk_tmp_dir_with_prefix(program_info.PROGRAM_NAME + '-'),
                 run_as_part_of_explicit_suite: Optional[pathlib.Path] = None,
                 ):
        self.__test_case_file_path = test_case_file_path
        self.__initial_hds_dir_path = initial_hds_dir_path
        self.__output = output
        self.__handling_setup = handling_setup
        self.__sandbox_root_dir_resolver = sandbox_root_dir_resolver
        self.__run_as_part_of_explicit_suite = run_as_part_of_explicit_suite

    @property
    def test_case_file_path(self) -> pathlib.Path:
        return self.__test_case_file_path

    @property
    def initial_hds_dir_path(self) -> pathlib.Path:
        return self.__initial_hds_dir_path

    @property
    def reporting_option(self) -> ReportingOption:
        return self.__output

    @property
    def handling_setup(self) -> TestCaseHandlingSetup:
        return self.__handling_setup

    @property
    def sandbox_root_dir_resolver(self) -> SandboxRootDirNameResolver:
        return self.__sandbox_root_dir_resolver

    @property
    def run_as_part_of_explicit_suite(self) -> Optional[pathlib.Path]:
        """
        If not None, the the file must exist as a suite and the test case is run as part of this suite
        """
        return self.__run_as_part_of_explicit_suite
